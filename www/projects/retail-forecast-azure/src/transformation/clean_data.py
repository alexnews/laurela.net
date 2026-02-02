"""Data cleaning and feature engineering"""
import json
import pandas as pd
from pathlib import Path
from glob import glob


class DataProcessor:
    def load_latest_raw(self, raw_dir: str = "data/raw") -> pd.DataFrame:
        files = sorted(glob(f"{raw_dir}/census_mrts_*.json"))
        if not files:
            raise FileNotFoundError(f"No raw files in {raw_dir}")

        latest = files[-1]
        print(f"Loading {latest}")

        with open(latest, 'r') as f:
            data = json.load(f)

        df = pd.DataFrame(data['data'])
        df['ds'] = pd.to_datetime(df['ds'])
        return df

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df = df.drop_duplicates(subset=['ds'], keep='last')
        df = df.dropna(subset=['y'])
        df = df.sort_values('ds').reset_index(drop=True)
        return df

    def add_features(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Time features
        df['year'] = df['ds'].dt.year
        df['month'] = df['ds'].dt.month
        df['quarter'] = df['ds'].dt.quarter
        df['is_holiday_month'] = df['month'].isin([11, 12])

        # Lag features
        df['sales_lag_1'] = df['y'].shift(1)
        df['sales_lag_12'] = df['y'].shift(12)
        df['rolling_mean_3'] = df['y'].rolling(3, min_periods=1).mean()
        df['yoy_growth'] = (df['y'] - df['sales_lag_12']) / df['sales_lag_12'] * 100

        return df

    def save(self, df: pd.DataFrame, output_dir: str = "data/processed") -> str:
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        filepath = Path(output_dir) / "retail_sales_clean.parquet"
        df.to_parquet(filepath, index=False)
        print(f"Saved to {filepath}")
        return str(filepath)


if __name__ == "__main__":
    processor = DataProcessor()
    df = processor.load_latest_raw()
    df = processor.clean(df)
    df = processor.add_features(df)
    processor.save(df)
    print(f"\nData shape: {df.shape}")
    print(df.tail())
