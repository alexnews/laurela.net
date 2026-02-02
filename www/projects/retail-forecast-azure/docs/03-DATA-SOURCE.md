# Census Bureau Data Source

This document details the U.S. Census Bureau Monthly Retail Trade Survey (MRTS) API.

## Overview

The Monthly Retail Trade Survey (MRTS) provides monthly estimates of retail sales in the United States. Data is released approximately 6 weeks after the reference month.

**Official Documentation:**
- Main page: https://www.census.gov/retail/index.html
- API guide: https://www2.census.gov/data/api-documentation/EITS_API_User_Guide_Dec2020.pdf
- Data sets: https://www.census.gov/data/developers/data-sets.html

## API Endpoint

```
Base URL: https://api.census.gov/data/timeseries/eits/mrts
```

## Authentication

The Census API requires a free API key:

1. Register at: https://api.census.gov/data/key_signup.html
2. Receive key via email (instant)
3. Include in requests: `?key=YOUR_API_KEY`

**Rate Limits:**
- 500 requests per day per key
- No per-minute throttling
- Recommended: Add 1-second delay between requests

## Available Data

### Category Codes (NAICS)

For this project, we focus on **Category 445: Food and Beverage Stores**.

| Code | Description | Subcategories |
|------|-------------|---------------|
| 445 | Food and Beverage Stores | All below |
| 4451 | Grocery Stores | Supermarkets, convenience stores |
| 44511 | Supermarkets and Grocery | Large format grocery |
| 44512 | Convenience Stores | Small format, gas stations |
| 4452 | Specialty Food Stores | Meat, fish, produce |
| 4453 | Beer, Wine, Liquor | Alcohol retailers |

**Other Popular Categories (for reference):**

| Code | Description |
|------|-------------|
| 441 | Motor Vehicle and Parts Dealers |
| 442 | Furniture and Home Furnishings |
| 443 | Electronics and Appliance Stores |
| 444 | Building Material and Garden |
| 446 | Health and Personal Care |
| 447 | Gasoline Stations |
| 448 | Clothing and Accessories |
| 452 | General Merchandise |
| 454 | Nonstore Retailers (e-commerce) |

### Data Type Codes

| Code | Description | Use Case |
|------|-------------|----------|
| SM | Sales - Monthly | Primary metric |
| SA | Sales - Annual | Year totals |
| SMSAM | Sales - Monthly, Seasonally Adjusted | Trend analysis |

### Time Slot Format

| Format | Example | Description |
|--------|---------|-------------|
| YYYY | 2023 | Full year |
| YYYYMM | 202312 | Specific month |
| from YYYY | from 2020 | All data from year |
| YYYY to YYYY | 2020 to 2024 | Date range |

## API Query Examples

### Basic Request

```bash
# Get monthly sales for Food & Beverage (445) from 2020
curl "https://api.census.gov/data/timeseries/eits/mrts?get=cell_value,time_slot_id,category_code&category_code=445&data_type_code=SM&time_slot_id=from+2020&key=YOUR_API_KEY"
```

### Response Format

```json
[
  ["cell_value", "time_slot_id", "category_code"],
  ["75432", "202001", "445"],
  ["72891", "202002", "445"],
  ["78234", "202003", "445"]
]
```

- First row is always headers
- `cell_value`: Sales in millions of dollars
- `time_slot_id`: YYYYMM format
- Values are strings (need conversion)

### Python Request Example

```python
import requests
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

def fetch_retail_data(category_code="445", start_year=2015):
    """
    Fetch monthly retail sales data from Census Bureau API.

    Args:
        category_code: NAICS category code
        start_year: First year to fetch

    Returns:
        pandas DataFrame with ds, y columns
    """
    API_KEY = os.getenv("CENSUS_API_KEY")
    BASE_URL = "https://api.census.gov/data/timeseries/eits/mrts"

    params = {
        "get": "cell_value,time_slot_id,category_code",
        "category_code": category_code,
        "data_type_code": "SM",  # Monthly Sales
        "time_slot_id": f"from {start_year}",
        "key": API_KEY
    }

    response = requests.get(BASE_URL, params=params)
    response.raise_for_status()

    data = response.json()

    # Convert to DataFrame
    df = pd.DataFrame(data[1:], columns=data[0])

    # Parse columns
    df['ds'] = pd.to_datetime(df['time_slot_id'], format='%Y%m')
    df['y'] = pd.to_numeric(df['cell_value'], errors='coerce')

    # Sort by date
    df = df.sort_values('ds').reset_index(drop=True)

    return df[['ds', 'y', 'category_code']]


if __name__ == "__main__":
    df = fetch_retail_data()
    print(f"Fetched {len(df)} records")
    print(df.head())
    print(df.tail())
```

## Data Schema

### Raw Data

```
census_mrts_YYYYMM.json
{
  "fetch_timestamp": "2024-01-15T10:30:00Z",
  "source": "Census Bureau MRTS API",
  "category_code": "445",
  "data_type_code": "SM",
  "records": [
    {
      "time_slot_id": "202312",
      "cell_value": "78234",
      "category_code": "445"
    }
  ]
}
```

### Processed Data

```
retail_sales_clean.parquet

Schema:
├── ds: datetime64[ns]      # Date (first of month)
├── y: float64              # Sales in millions USD
├── category_code: string   # NAICS code
├── year: int64             # Year extracted
├── month: int64            # Month extracted
├── quarter: int64          # Quarter (1-4)
├── is_holiday_month: bool  # Nov, Dec = True
├── days_in_month: int64    # Number of days
├── sales_lag_1: float64    # Previous month sales
├── sales_lag_12: float64   # Same month last year
├── rolling_mean_3: float64 # 3-month rolling average
├── yoy_growth: float64     # Year-over-year % change
```

## Data Quality Notes

### Known Issues

1. **Revisions:** Initial releases are estimates; revised data comes 1-2 months later
2. **Seasonal Adjustment:** Raw data (`SM`) is not seasonally adjusted
3. **Missing Data:** Rare, but some months may have null values
4. **COVID Impact:** 2020-2021 data shows unusual patterns

### Handling Missing Data

```python
def clean_missing_values(df):
    """
    Handle missing values in retail sales data.
    """
    # Check for nulls
    null_count = df['y'].isna().sum()
    if null_count > 0:
        print(f"Warning: {null_count} missing values found")

        # Option 1: Forward fill (use previous month)
        df['y'] = df['y'].fillna(method='ffill')

        # Option 2: Interpolate (linear between points)
        # df['y'] = df['y'].interpolate(method='linear')

    return df
```

## Data Exploration

### Sample Analysis Script

```python
import pandas as pd
import matplotlib.pyplot as plt

def explore_data(df):
    """
    Basic exploratory analysis of retail sales data.
    """
    print("=== Data Overview ===")
    print(f"Date range: {df['ds'].min()} to {df['ds'].max()}")
    print(f"Total records: {len(df)}")
    print(f"Missing values: {df['y'].isna().sum()}")

    print("\n=== Summary Statistics ===")
    print(df['y'].describe())

    print("\n=== Year-over-Year Growth ===")
    yearly = df.groupby(df['ds'].dt.year)['y'].sum()
    growth = yearly.pct_change() * 100
    print(growth.round(2))

    # Plot time series
    plt.figure(figsize=(12, 6))
    plt.plot(df['ds'], df['y'])
    plt.title('Monthly Retail Sales - Food & Beverage Stores')
    plt.xlabel('Date')
    plt.ylabel('Sales (Millions USD)')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('data/processed/sales_timeseries.png')
    plt.show()

    return df
```

## Historical Context

### Key Events Affecting Data

| Period | Event | Impact on Food & Beverage |
|--------|-------|---------------------------|
| Mar 2020 | COVID-19 lockdowns | Initial spike (panic buying) |
| Apr-May 2020 | Restaurant closures | Sustained grocery increase |
| 2021 | Vaccine rollout | Gradual normalization |
| 2022 | Inflation surge | Price increases boost $ sales |
| 2023 | Stabilization | Return to trend |

### Holiday Effects

| Month | Holiday | Expected Impact |
|-------|---------|-----------------|
| November | Thanksgiving | +15-20% vs average |
| December | Christmas/Hanukkah | +20-25% vs average |
| February | Super Bowl | +5-10% for specific categories |
| July | Independence Day | +5-10% for beverages |

## Data Freshness

The Census Bureau releases data on a fixed schedule:

- **Advance Monthly:** ~2 weeks after month end (preliminary)
- **Monthly Retail Trade:** ~6 weeks after month end (revised)

Check release schedule: https://www.census.gov/economic-indicators/calendar-listview.html

## Additional Data Sources (Optional Enrichment)

### Federal Reserve Economic Data (FRED)

| Series | Description | Use |
|--------|-------------|-----|
| CPIAUCSL | Consumer Price Index | Adjust for inflation |
| UNRATE | Unemployment Rate | Economic context |
| RSXFS | Retail Sales Ex Food Services | Comparison |

**Access:** https://fred.stlouisfed.org/

### Bureau of Labor Statistics

| Data | Description | Use |
|------|-------------|-----|
| CPI Food at Home | Food price index | Price adjustment |
| Employment data | Retail sector jobs | Context |

## Next Steps

1. [Build the ETL pipeline](04-ETL-PIPELINE.md)
2. [Configure forecasting model](05-FORECASTING.md)
