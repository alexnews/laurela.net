"""Census Bureau MRTS API Data Extractor"""
import os
import json
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class CensusExtractor:
    BASE_URL = "https://api.census.gov/data/timeseries/eits/mrts"

    def __init__(self, category_code: str = "445"):
        self.api_key = os.getenv("CENSUS_API_KEY")
        if not self.api_key:
            raise ValueError("CENSUS_API_KEY not set in .env")
        self.category_code = category_code

    def fetch_data(self, start_year: int = 2015) -> pd.DataFrame:
        params = {
            "get": "cell_value,time_slot_id,category_code",
            "category_code": self.category_code,
            "data_type_code": "SM",
            "seasonally_adj": "no",
            "time": f"from {start_year}",
            "key": self.api_key
        }

        print(f"Fetching data from Census API...")
        response = requests.get(self.BASE_URL, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()
        df = pd.DataFrame(data[1:], columns=data[0])

        # Handle duplicate column names
        df = df.loc[:, ~df.columns.duplicated()]

        # Date is in 'time' column (format: YYYY-MM)
        df['ds'] = pd.to_datetime(df['time'], format='%Y-%m')
        df['y'] = pd.to_numeric(df['cell_value'], errors='coerce')
        df = df.sort_values('ds').reset_index(drop=True)

        print(f"Fetched {len(df)} records from {df['ds'].min()} to {df['ds'].max()}")
        return df[['ds', 'y', 'category_code']]

    def save_raw(self, df: pd.DataFrame, output_dir: str = "data/raw") -> str:
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = Path(output_dir) / f"census_mrts_{timestamp}.json"

        output = {
            "fetch_timestamp": datetime.now().isoformat(),
            "source": "Census Bureau MRTS API",
            "category_code": self.category_code,
            "record_count": len(df),
            "data": df.to_dict(orient='records')
        }

        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2, default=str)

        print(f"Saved to {filepath}")
        return str(filepath)


if __name__ == "__main__":
    extractor = CensusExtractor()
    df = extractor.fetch_data()
    extractor.save_raw(df)
