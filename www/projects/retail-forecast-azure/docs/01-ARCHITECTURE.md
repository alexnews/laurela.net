# System Architecture

## Overview

This document describes the end-to-end architecture of the Retail Sales Forecasting System.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           RETAIL SALES FORECASTING SYSTEM                    │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐    ┌────────────┐ │
│  │   EXTRACT    │───▶│  TRANSFORM   │───▶│    TRAIN     │───▶│  VISUALIZE │ │
│  │              │    │              │    │              │    │            │ │
│  │ Census API   │    │ Clean Data   │    │   Prophet    │    │  Power BI  │ │
│  │              │    │ Feature Eng  │    │   Model      │    │  Dashboard │ │
│  └──────────────┘    └──────────────┘    └──────────────┘    └────────────┘ │
│         │                   │                   │                   │        │
│         ▼                   ▼                   ▼                   ▼        │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                         DATA STORAGE                                  │   │
│  │  raw/ ─────────────▶ processed/ ─────────────▶ predictions/          │   │
│  │  (JSON/CSV)          (Parquet)                (CSV + JSON)            │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                      ORCHESTRATION LAYER                              │   │
│  │           Azure Data Factory  OR  Apache Airflow                      │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Data Extraction Layer

**Source:** U.S. Census Bureau Economic Indicators Time Series (EITS) API

```
┌─────────────────────────────────────────────────┐
│              CENSUS BUREAU API                   │
│  https://api.census.gov/data/timeseries/eits   │
├─────────────────────────────────────────────────┤
│  Endpoint: /mrts                                │
│  Format: JSON                                   │
│  Auth: API Key (free registration)              │
│  Rate Limit: 500 requests/day                   │
│  Data: Monthly Retail Trade Survey              │
└─────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────┐
│           INGESTION SCRIPT                       │
│  src/ingestion/census_extractor.py              │
├─────────────────────────────────────────────────┤
│  - Handles API authentication                   │
│  - Manages rate limiting                         │
│  - Implements retry logic                        │
│  - Validates response data                       │
│  - Saves to data/raw/                           │
└─────────────────────────────────────────────────┘
```

### 2. Data Transformation Layer

```
┌─────────────────────────────────────────────────┐
│           RAW DATA (data/raw/)                   │
│  census_mrts_YYYYMM.json                        │
├─────────────────────────────────────────────────┤
│  - Raw API response                              │
│  - Multiple retail categories                    │
│  - String data types                             │
│  - May contain nulls                             │
└─────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────┐
│           TRANSFORMATION PIPELINE                │
│  src/transformation/                             │
├─────────────────────────────────────────────────┤
│  clean_data.py                                   │
│  ├── Parse dates to datetime                    │
│  ├── Convert sales to numeric                   │
│  ├── Handle missing values                      │
│  └── Filter to target category (NAICS 445)      │
│                                                  │
│  feature_engineering.py                          │
│  ├── Add time-based features                    │
│  │   ├── month, quarter, year                   │
│  │   ├── is_holiday_month                       │
│  │   └── days_in_month                          │
│  ├── Add lag features                           │
│  │   ├── sales_lag_1 (previous month)           │
│  │   ├── sales_lag_12 (same month last year)    │
│  │   └── rolling_mean_3m                        │
│  └── Add economic indicators (optional)         │
│      ├── cpi_index                              │
│      └── unemployment_rate                       │
└─────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────┐
│        PROCESSED DATA (data/processed/)          │
│  retail_sales_clean.parquet                     │
├─────────────────────────────────────────────────┤
│  Schema:                                         │
│  ├── ds: datetime (date)                        │
│  ├── y: float64 (sales in millions)             │
│  ├── category: string (NAICS code)              │
│  ├── month: int                                  │
│  ├── year: int                                   │
│  ├── is_holiday: bool                           │
│  └── [lag features...]                          │
└─────────────────────────────────────────────────┘
```

### 3. Forecasting Layer

```
┌─────────────────────────────────────────────────┐
│              PROPHET MODEL                       │
│  src/forecasting/prophet_model.py               │
├─────────────────────────────────────────────────┤
│                                                  │
│  Model Configuration:                            │
│  ├── seasonality_mode: 'multiplicative'         │
│  ├── yearly_seasonality: True                   │
│  ├── weekly_seasonality: False (monthly data)   │
│  ├── changepoint_prior_scale: 0.05              │
│  └── interval_width: 0.95                       │
│                                                  │
│  Custom Components:                              │
│  ├── US Holidays (Thanksgiving, Christmas)      │
│  ├── COVID-19 impact regressor (2020-2021)      │
│  └── Inflation adjustment regressor             │
│                                                  │
│  Outputs:                                        │
│  ├── yhat: point forecast                       │
│  ├── yhat_lower: lower confidence bound         │
│  ├── yhat_upper: upper confidence bound         │
│  ├── trend: long-term trend component           │
│  └── yearly: seasonal component                 │
│                                                  │
└─────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────┐
│       PREDICTIONS (data/predictions/)            │
│  forecast_YYYYMMDD.csv                          │
├─────────────────────────────────────────────────┤
│  Columns:                                        │
│  ├── ds: date                                   │
│  ├── yhat: predicted value                      │
│  ├── yhat_lower_80: 80% confidence lower        │
│  ├── yhat_upper_80: 80% confidence upper        │
│  ├── yhat_lower_95: 95% confidence lower        │
│  ├── yhat_upper_95: 95% confidence upper        │
│  └── model_version: string                      │
└─────────────────────────────────────────────────┘
```

### 4. Visualization Layer

```
┌─────────────────────────────────────────────────┐
│              POWER BI DASHBOARD                  │
│  dashboards/retail_forecast.pbix                │
├─────────────────────────────────────────────────┤
│                                                  │
│  Data Sources:                                   │
│  ├── processed/retail_sales_clean.parquet       │
│  └── predictions/forecast_latest.csv            │
│                                                  │
│  Pages:                                          │
│  ├── 1. Executive Summary                       │
│  │   └── KPIs, trend, next month forecast       │
│  ├── 2. Historical Analysis                     │
│  │   └── YoY comparison, growth rates           │
│  ├── 3. Forecast Detail                         │
│  │   └── Predictions with confidence bands      │
│  ├── 4. Seasonality                             │
│  │   └── Decomposition, pattern analysis        │
│  └── 5. Model Performance                       │
│      └── Errors, anomalies, explanations        │
│                                                  │
└─────────────────────────────────────────────────┘
           │
           ▼
┌─────────────────────────────────────────────────┐
│              GITHUB PAGES                        │
│  https://alexdata.github.io/retail-forecast    │
├─────────────────────────────────────────────────┤
│  Static exports:                                 │
│  ├── Dashboard screenshots (PNG)                │
│  ├── Interactive charts (Plotly HTML)           │
│  └── PDF report                                 │
└─────────────────────────────────────────────────┘
```

## Orchestration Options

### Option A: Azure Data Factory (Production)

```
┌──────────────────────────────────────────────────────────────────────┐
│                     AZURE DATA FACTORY PIPELINE                       │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐           │
│  │ Trigger │───▶│ Extract │───▶│Transform│───▶│Forecast │           │
│  │ (Daily) │    │ Census  │    │  Data   │    │ Prophet │           │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘           │
│                      │              │              │                  │
│                      ▼              ▼              ▼                  │
│               ┌─────────────────────────────────────────┐            │
│               │         AZURE BLOB STORAGE               │            │
│               │  raw/ ─────▶ processed/ ─────▶ output/  │            │
│               └─────────────────────────────────────────┘            │
│                                                                       │
│  Activities:                                                          │
│  ├── Web Activity: Call Census API                                   │
│  ├── Copy Activity: Store raw data                                   │
│  ├── Databricks/Azure Functions: Python transformation               │
│  └── Azure Functions: Prophet forecasting                            │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

### Option B: Apache Airflow (Open Source)

```
┌──────────────────────────────────────────────────────────────────────┐
│                        AIRFLOW DAG                                    │
│  dags/retail_forecast_dag.py                                         │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  Schedule: @monthly (1st of each month)                              │
│                                                                       │
│  ┌─────────────┐                                                     │
│  │   start     │                                                     │
│  └──────┬──────┘                                                     │
│         │                                                             │
│         ▼                                                             │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐              │
│  │   extract   │───▶│  transform  │───▶│   forecast  │              │
│  │  _census    │    │   _data     │    │   _prophet  │              │
│  └─────────────┘    └─────────────┘    └─────────────┘              │
│         │                                     │                       │
│         │                                     ▼                       │
│         │                            ┌─────────────┐                 │
│         │                            │   export    │                 │
│         │                            │  _results   │                 │
│         │                            └──────┬──────┘                 │
│         │                                   │                         │
│         ▼                                   ▼                         │
│  ┌──────────────────────────────────────────────────┐                │
│  │              LOCAL FILE SYSTEM                    │                │
│  │    data/raw/ ─────▶ data/processed/ ─────▶ data/predictions/     │
│  └──────────────────────────────────────────────────┘                │
│                                                                       │
│  Operators Used:                                                      │
│  ├── PythonOperator: All data processing                             │
│  ├── BashOperator: File management                                   │
│  └── EmailOperator: Notifications (optional)                         │
│                                                                       │
└──────────────────────────────────────────────────────────────────────┘
```

## Data Flow Summary

```
Census Bureau API
       │
       │ (1) HTTP GET /mrts?get=cell_value&category_code=445
       ▼
┌──────────────┐
│  Raw JSON    │  data/raw/census_mrts_202401.json
└──────┬───────┘
       │
       │ (2) Parse, clean, validate
       ▼
┌──────────────┐
│   Cleaned    │  data/processed/retail_sales_clean.parquet
│   Parquet    │
└──────┬───────┘
       │
       │ (3) Feature engineering, split train/test
       ▼
┌──────────────┐
│  Train Data  │  ds, y columns for Prophet
└──────┬───────┘
       │
       │ (4) Fit Prophet model
       ▼
┌──────────────┐
│   Model      │  models/prophet_model.pkl
└──────┬───────┘
       │
       │ (5) Generate 6-month forecast
       ▼
┌──────────────┐
│ Predictions  │  data/predictions/forecast_20240101.csv
└──────┬───────┘
       │
       │ (6) Load into Power BI
       ▼
┌──────────────┐
│  Dashboard   │  dashboards/retail_forecast.pbix
└──────┬───────┘
       │
       │ (7) Export static assets
       ▼
┌──────────────┐
│ GitHub Pages │  Static HTML, PNG, PDF
└──────────────┘
```

## Security Considerations

| Component | Security Measure |
|-----------|------------------|
| Census API Key | Store in environment variable or Azure Key Vault |
| Azure credentials | Use Managed Identity or Service Principal |
| Data files | .gitignore raw data, commit only schemas |
| Power BI | Publish to web with row-level security disabled (public data) |

## Scalability Notes

This architecture is designed for **single-category monthly data**. To scale:

1. **Multiple categories**: Parameterize pipeline, loop through NAICS codes
2. **Daily granularity**: Requires different data source (private retail data)
3. **Real-time updates**: Replace batch with streaming (Azure Stream Analytics)

## Next Steps

1. [Set up your environment](02-SETUP.md)
2. [Configure data source access](03-DATA-SOURCE.md)
3. [Build the ETL pipeline](04-ETL-PIPELINE.md)
