# ETL Pipeline Documentation

This guide covers building the data pipeline using either Azure Data Factory or Apache Airflow.

## Pipeline Overview

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   EXTRACT   │───▶│  TRANSFORM  │───▶│   FORECAST  │───▶│   EXPORT    │
│  Census API │    │  Clean Data │    │   Prophet   │    │  Dashboard  │
└─────────────┘    └─────────────┘    └─────────────┘    └─────────────┘
```

**Schedule:** Monthly (1st of each month at 6:00 AM UTC)

---

## Option A: Apache Airflow (Recommended for Portfolio)

Airflow is open-source and demonstrates DevOps skills without cloud costs.

### Project Structure

```
project_01_retail_forecast/
├── dags/
│   └── retail_forecast_dag.py
├── src/
│   ├── __init__.py
│   ├── ingestion/
│   │   ├── __init__.py
│   │   └── census_extractor.py
│   ├── transformation/
│   │   ├── __init__.py
│   │   ├── clean_data.py
│   │   └── feature_engineering.py
│   ├── forecasting/
│   │   ├── __init__.py
│   │   └── prophet_model.py
│   └── utils/
│       ├── __init__.py
│       └── config.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── predictions/
└── docker-compose.yaml
```

### Step 1: Create Extraction Module

**`src/ingestion/census_extractor.py`**

```python
"""
Census Bureau MRTS API Data Extractor
"""
import os
import json
import requests
import pandas as pd
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class CensusExtractor:
    """Extract retail sales data from Census Bureau API."""

    BASE_URL = "https://api.census.gov/data/timeseries/eits/mrts"

    def __init__(self, category_code: str = "445"):
        self.api_key = os.getenv("CENSUS_API_KEY")
        if not self.api_key:
            raise ValueError("CENSUS_API_KEY environment variable not set")
        self.category_code = category_code

    def fetch_data(self, start_year: int = 2015) -> pd.DataFrame:
        """
        Fetch monthly retail sales data.

        Args:
            start_year: First year to fetch data from

        Returns:
            DataFrame with columns: ds, y, category_code
        """
        params = {
            "get": "cell_value,time_slot_id,category_code",
            "category_code": self.category_code,
            "data_type_code": "SM",
            "time_slot_id": f"from {start_year}",
            "key": self.api_key
        }

        response = requests.get(self.BASE_URL, params=params, timeout=30)
        response.raise_for_status()

        data = response.json()

        # First row is headers
        df = pd.DataFrame(data[1:], columns=data[0])

        # Parse and convert
        df['ds'] = pd.to_datetime(df['time_slot_id'], format='%Y%m')
        df['y'] = pd.to_numeric(df['cell_value'], errors='coerce')

        df = df.sort_values('ds').reset_index(drop=True)

        return df[['ds', 'y', 'category_code']]

    def save_raw(self, df: pd.DataFrame, output_dir: str = "data/raw") -> str:
        """
        Save raw data with metadata.

        Returns:
            Path to saved file
        """
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"census_mrts_{timestamp}.json"
        filepath = Path(output_dir) / filename

        output = {
            "fetch_timestamp": datetime.now().isoformat(),
            "source": "Census Bureau MRTS API",
            "category_code": self.category_code,
            "record_count": len(df),
            "date_range": {
                "start": df['ds'].min().isoformat(),
                "end": df['ds'].max().isoformat()
            },
            "data": df.to_dict(orient='records')
        }

        with open(filepath, 'w') as f:
            json.dump(output, f, indent=2, default=str)

        print(f"Saved {len(df)} records to {filepath}")
        return str(filepath)


def extract_census_data(**context):
    """Airflow callable function."""
    extractor = CensusExtractor(category_code="445")
    df = extractor.fetch_data(start_year=2015)
    filepath = extractor.save_raw(df)

    # Push to XCom for next task
    context['ti'].xcom_push(key='raw_file_path', value=filepath)
    context['ti'].xcom_push(key='record_count', value=len(df))

    return filepath


if __name__ == "__main__":
    # Test extraction
    extractor = CensusExtractor()
    df = extractor.fetch_data()
    print(df.head())
    extractor.save_raw(df)
```

### Step 2: Create Transformation Module

**`src/transformation/clean_data.py`**

```python
"""
Data cleaning and validation
"""
import json
import pandas as pd
from pathlib import Path
from datetime import datetime


class DataCleaner:
    """Clean and validate retail sales data."""

    def __init__(self):
        self.validation_errors = []

    def load_raw(self, filepath: str) -> pd.DataFrame:
        """Load raw JSON data."""
        with open(filepath, 'r') as f:
            data = json.load(f)

        df = pd.DataFrame(data['data'])
        df['ds'] = pd.to_datetime(df['ds'])
        return df

    def validate(self, df: pd.DataFrame) -> bool:
        """
        Validate data quality.

        Returns:
            True if validation passes
        """
        self.validation_errors = []

        # Check for nulls
        null_count = df['y'].isna().sum()
        if null_count > 0:
            self.validation_errors.append(f"Found {null_count} null values")

        # Check for negative values
        negative_count = (df['y'] < 0).sum()
        if negative_count > 0:
            self.validation_errors.append(f"Found {negative_count} negative values")

        # Check date continuity
        df_sorted = df.sort_values('ds')
        expected_months = pd.date_range(
            start=df_sorted['ds'].min(),
            end=df_sorted['ds'].max(),
            freq='MS'
        )
        missing_months = set(expected_months) - set(df_sorted['ds'])
        if missing_months:
            self.validation_errors.append(
                f"Missing {len(missing_months)} months: {sorted(missing_months)[:5]}"
            )

        # Check for outliers (3 sigma)
        mean = df['y'].mean()
        std = df['y'].std()
        outliers = df[(df['y'] < mean - 3*std) | (df['y'] > mean + 3*std)]
        if len(outliers) > 0:
            # Log but don't fail - outliers may be valid (COVID, holidays)
            print(f"Note: {len(outliers)} potential outliers detected")

        return len(self.validation_errors) == 0

    def clean(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean the data.

        - Handle missing values
        - Remove duplicates
        - Sort by date
        """
        df = df.copy()

        # Remove duplicates (keep latest)
        df = df.drop_duplicates(subset=['ds'], keep='last')

        # Handle missing values (forward fill)
        if df['y'].isna().any():
            df['y'] = df['y'].fillna(method='ffill')

        # Sort by date
        df = df.sort_values('ds').reset_index(drop=True)

        return df

    def save_processed(self, df: pd.DataFrame, output_dir: str = "data/processed") -> str:
        """Save cleaned data as Parquet."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        filepath = Path(output_dir) / "retail_sales_clean.parquet"
        df.to_parquet(filepath, index=False)

        print(f"Saved cleaned data to {filepath}")
        return str(filepath)


def clean_data(**context):
    """Airflow callable function."""
    ti = context['ti']
    raw_file_path = ti.xcom_pull(key='raw_file_path', task_ids='extract_census')

    cleaner = DataCleaner()
    df = cleaner.load_raw(raw_file_path)

    if not cleaner.validate(df):
        print(f"Validation warnings: {cleaner.validation_errors}")

    df_clean = cleaner.clean(df)
    filepath = cleaner.save_processed(df_clean)

    ti.xcom_push(key='clean_file_path', value=filepath)

    return filepath
```

**`src/transformation/feature_engineering.py`**

```python
"""
Feature engineering for forecasting
"""
import pandas as pd
from pathlib import Path


class FeatureEngineer:
    """Add features for Prophet model."""

    def __init__(self):
        self.holidays = self._get_us_holidays()

    def _get_us_holidays(self) -> pd.DataFrame:
        """
        Get US holidays relevant to retail.

        Returns:
            DataFrame for Prophet holidays parameter
        """
        # Major retail holidays
        holidays = []

        for year in range(2015, 2030):
            # Thanksgiving (4th Thursday of November)
            thanksgiving = pd.Timestamp(year, 11, 1) + pd.offsets.Week(weekday=3) + pd.offsets.Week(3)
            holidays.append({
                'holiday': 'thanksgiving',
                'ds': thanksgiving,
                'lower_window': -1,  # Day before
                'upper_window': 1   # Day after
            })

            # Christmas
            holidays.append({
                'holiday': 'christmas',
                'ds': pd.Timestamp(year, 12, 25),
                'lower_window': -7,  # Week before
                'upper_window': 1
            })

            # New Year
            holidays.append({
                'holiday': 'new_year',
                'ds': pd.Timestamp(year, 1, 1),
                'lower_window': -1,
                'upper_window': 0
            })

            # Independence Day
            holidays.append({
                'holiday': 'july_4th',
                'ds': pd.Timestamp(year, 7, 4),
                'lower_window': -1,
                'upper_window': 1
            })

        return pd.DataFrame(holidays)

    def add_time_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add time-based features."""
        df = df.copy()

        df['year'] = df['ds'].dt.year
        df['month'] = df['ds'].dt.month
        df['quarter'] = df['ds'].dt.quarter
        df['day_of_year'] = df['ds'].dt.dayofyear

        # Holiday months
        df['is_holiday_month'] = df['month'].isin([11, 12])

        # Days in month (affects total sales)
        df['days_in_month'] = df['ds'].dt.days_in_month

        return df

    def add_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add lagged features."""
        df = df.copy()
        df = df.sort_values('ds')

        # Previous month
        df['sales_lag_1'] = df['y'].shift(1)

        # Same month last year
        df['sales_lag_12'] = df['y'].shift(12)

        # Rolling averages
        df['rolling_mean_3'] = df['y'].rolling(window=3, min_periods=1).mean()
        df['rolling_mean_6'] = df['y'].rolling(window=6, min_periods=1).mean()
        df['rolling_mean_12'] = df['y'].rolling(window=12, min_periods=1).mean()

        # Year-over-year growth
        df['yoy_growth'] = (df['y'] - df['sales_lag_12']) / df['sales_lag_12'] * 100

        return df

    def add_covid_indicator(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add COVID-19 impact indicator."""
        df = df.copy()

        # COVID impact periods
        df['covid_lockdown'] = (
            (df['ds'] >= '2020-03-01') & (df['ds'] <= '2020-06-01')
        ).astype(int)

        df['covid_recovery'] = (
            (df['ds'] >= '2020-06-01') & (df['ds'] <= '2021-06-01')
        ).astype(int)

        return df

    def prepare_prophet_data(self, df: pd.DataFrame) -> tuple:
        """
        Prepare data for Prophet.

        Returns:
            (train_df, future_df, holidays_df)
        """
        # Prophet requires 'ds' and 'y' columns
        prophet_df = df[['ds', 'y']].copy()

        return prophet_df, self.holidays

    def save_features(self, df: pd.DataFrame, output_dir: str = "data/processed") -> str:
        """Save feature-engineered data."""
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        filepath = Path(output_dir) / "retail_sales_features.parquet"
        df.to_parquet(filepath, index=False)

        # Also save holidays for Prophet
        holidays_path = Path(output_dir) / "holidays.parquet"
        self.holidays.to_parquet(holidays_path, index=False)

        print(f"Saved features to {filepath}")
        return str(filepath)


def engineer_features(**context):
    """Airflow callable function."""
    ti = context['ti']
    clean_file_path = ti.xcom_pull(key='clean_file_path', task_ids='clean_data')

    df = pd.read_parquet(clean_file_path)

    engineer = FeatureEngineer()
    df = engineer.add_time_features(df)
    df = engineer.add_lag_features(df)
    df = engineer.add_covid_indicator(df)

    filepath = engineer.save_features(df)

    ti.xcom_push(key='features_file_path', value=filepath)

    return filepath
```

### Step 3: Create Airflow DAG

**`dags/retail_forecast_dag.py`**

```python
"""
Retail Sales Forecasting DAG

Schedule: Monthly on 1st at 6:00 AM UTC
"""
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator

# Import task functions
import sys
sys.path.insert(0, '/opt/airflow/src')

from ingestion.census_extractor import extract_census_data
from transformation.clean_data import clean_data
from transformation.feature_engineering import engineer_features
from forecasting.prophet_model import train_and_forecast

# Default arguments
default_args = {
    'owner': 'alex',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# DAG definition
with DAG(
    dag_id='retail_sales_forecast',
    default_args=default_args,
    description='Monthly retail sales forecasting pipeline',
    schedule_interval='0 6 1 * *',  # 1st of month at 6 AM
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=['retail', 'forecasting', 'census'],
) as dag:

    # Task 1: Extract data from Census API
    extract_task = PythonOperator(
        task_id='extract_census',
        python_callable=extract_census_data,
        provide_context=True,
    )

    # Task 2: Clean and validate data
    clean_task = PythonOperator(
        task_id='clean_data',
        python_callable=clean_data,
        provide_context=True,
    )

    # Task 3: Feature engineering
    feature_task = PythonOperator(
        task_id='engineer_features',
        python_callable=engineer_features,
        provide_context=True,
    )

    # Task 4: Train model and generate forecasts
    forecast_task = PythonOperator(
        task_id='train_forecast',
        python_callable=train_and_forecast,
        provide_context=True,
    )

    # Task 5: Export results
    export_task = BashOperator(
        task_id='export_results',
        bash_command='''
            echo "Pipeline completed at $(date)"
            echo "Results saved to data/predictions/"
            ls -la /opt/airflow/data/predictions/
        ''',
    )

    # Task dependencies
    extract_task >> clean_task >> feature_task >> forecast_task >> export_task
```

### Step 4: Run the Pipeline

```bash
# Start Airflow (if not already running)
docker-compose up -d

# Access Airflow UI
open http://localhost:8080

# Enable the DAG
# 1. Find 'retail_sales_forecast' in the DAG list
# 2. Toggle the switch to enable it
# 3. Click the play button to trigger manually

# Or trigger via CLI
docker-compose exec airflow-webserver airflow dags trigger retail_sales_forecast

# Monitor logs
docker-compose logs -f airflow-scheduler
```

---

## Option B: Azure Data Factory

For production environments with Azure infrastructure.

### Step 1: Create Linked Services

**Linked Service: Census API**

```json
{
    "name": "ls_census_api",
    "type": "RestService",
    "typeProperties": {
        "url": "https://api.census.gov/data/timeseries/eits/mrts",
        "enableServerCertificateValidation": true,
        "authenticationType": "Anonymous"
    }
}
```

**Linked Service: Azure Blob Storage**

```json
{
    "name": "ls_azure_storage",
    "type": "AzureBlobStorage",
    "typeProperties": {
        "connectionString": {
            "type": "AzureKeyVaultSecret",
            "store": {
                "referenceName": "ls_keyvault",
                "type": "LinkedServiceReference"
            },
            "secretName": "storage-connection-string"
        }
    }
}
```

### Step 2: Create Datasets

**Dataset: Census API Response**

```json
{
    "name": "ds_census_response",
    "type": "RestResource",
    "linkedServiceName": {
        "referenceName": "ls_census_api",
        "type": "LinkedServiceReference"
    },
    "typeProperties": {
        "relativeUrl": "?get=cell_value,time_slot_id,category_code&category_code=445&data_type_code=SM&time_slot_id=from+2015&key=@{pipeline().parameters.api_key}"
    }
}
```

**Dataset: Raw Data Blob**

```json
{
    "name": "ds_raw_json",
    "type": "Json",
    "linkedServiceName": {
        "referenceName": "ls_azure_storage",
        "type": "LinkedServiceReference"
    },
    "typeProperties": {
        "location": {
            "type": "AzureBlobStorageLocation",
            "container": "raw",
            "fileName": {
                "value": "@concat('census_mrts_', formatDateTime(utcnow(), 'yyyyMMdd'), '.json')",
                "type": "Expression"
            }
        }
    }
}
```

### Step 3: Create Pipeline

**Pipeline: pl_retail_forecast**

```json
{
    "name": "pl_retail_forecast",
    "properties": {
        "activities": [
            {
                "name": "Extract Census Data",
                "type": "Copy",
                "inputs": [{"referenceName": "ds_census_response", "type": "DatasetReference"}],
                "outputs": [{"referenceName": "ds_raw_json", "type": "DatasetReference"}],
                "typeProperties": {
                    "source": {"type": "RestSource"},
                    "sink": {"type": "JsonSink"}
                }
            },
            {
                "name": "Transform Data",
                "type": "DatabricksNotebook",
                "dependsOn": [{"activity": "Extract Census Data", "dependencyConditions": ["Succeeded"]}],
                "typeProperties": {
                    "notebookPath": "/notebooks/transform_retail_data"
                }
            },
            {
                "name": "Run Forecast",
                "type": "AzureFunctionActivity",
                "dependsOn": [{"activity": "Transform Data", "dependencyConditions": ["Succeeded"]}],
                "typeProperties": {
                    "functionName": "ProphetForecast",
                    "method": "POST"
                }
            }
        ],
        "parameters": {
            "api_key": {"type": "string"}
        }
    }
}
```

### Step 4: Create Trigger

```json
{
    "name": "tr_monthly_forecast",
    "type": "ScheduleTrigger",
    "typeProperties": {
        "recurrence": {
            "frequency": "Month",
            "interval": 1,
            "startTime": "2024-01-01T06:00:00Z",
            "schedule": {
                "monthDays": [1]
            }
        }
    },
    "pipelines": [
        {
            "pipelineReference": {
                "referenceName": "pl_retail_forecast",
                "type": "PipelineReference"
            },
            "parameters": {
                "api_key": "@{linkedService.ls_keyvault.getSecret('census-api-key')}"
            }
        }
    ]
}
```

### Step 5: Deploy with ARM Template

```bash
# Deploy ADF resources
az deployment group create \
  --resource-group rg-retail-forecast \
  --template-file pipelines/adf/arm_template.json \
  --parameters pipelines/adf/arm_parameters.json
```

---

## Pipeline Monitoring

### Airflow Monitoring

```python
# Check DAG status
docker-compose exec airflow-webserver airflow dags list-runs -d retail_sales_forecast

# View task logs
docker-compose exec airflow-webserver airflow tasks logs retail_sales_forecast extract_census 2024-01-01

# Check XCom values
docker-compose exec airflow-webserver airflow tasks render retail_sales_forecast extract_census 2024-01-01
```

### ADF Monitoring

```bash
# Check pipeline runs
az datafactory pipeline-run query-by-factory \
  --resource-group rg-retail-forecast \
  --factory-name adf-retail-forecast \
  --last-updated-after "2024-01-01T00:00:00Z"

# View activity runs
az datafactory activity-run query-by-pipeline-run \
  --resource-group rg-retail-forecast \
  --factory-name adf-retail-forecast \
  --run-id "<run-id>"
```

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| API 429 | Rate limit exceeded | Add retry with exponential backoff |
| API 500 | Census server issue | Retry after 5 minutes |
| Empty response | No new data | Skip pipeline, log warning |
| Validation fail | Data quality issue | Send alert, use previous data |

### Retry Logic

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=60)
)
def fetch_with_retry():
    return extractor.fetch_data()
```

## Next Steps

1. [Configure Prophet forecasting](05-FORECASTING.md)
2. [Build Power BI dashboard](06-DASHBOARD.md)
