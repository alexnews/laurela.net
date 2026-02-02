# Retail Sales Forecasting System

End-to-end data engineering and forecasting project using U.S. Census Bureau retail data.

## Project Overview

This project demonstrates a complete data pipeline that:
- **Ingests** monthly retail sales data from the U.S. Census Bureau API
- **Transforms** raw data into analysis-ready format
- **Trains** a Prophet forecasting model
- **Predicts** next-month sales with confidence intervals
- **Visualizes** results in an interactive Power BI dashboard

### Key Differentiator
Beyond just predictions, this project explains **why forecasts fail** — analyzing the impact of holidays, economic shocks, and seasonal patterns on prediction accuracy.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Data Source | U.S. Census Bureau MRTS API |
| Orchestration | Azure Data Factory / Apache Airflow |
| Processing | Python (pandas, requests) |
| Forecasting | Facebook Prophet |
| Visualization | Power BI |
| Hosting | GitHub Pages |

## Project Structure

```
project_01_retail_forecast/
├── README.md                    # This file
├── docs/
│   ├── 01-ARCHITECTURE.md       # System design & data flow
│   ├── 02-SETUP.md              # Environment setup guide
│   ├── 03-DATA-SOURCE.md        # Census API documentation
│   ├── 04-ETL-PIPELINE.md       # Pipeline configuration
│   ├── 05-FORECASTING.md        # Prophet model guide
│   ├── 06-DASHBOARD.md          # Power BI dashboard design
│   └── 07-DEPLOYMENT.md         # GitHub Pages deployment
├── src/
│   ├── ingestion/               # Data extraction scripts
│   ├── transformation/          # Data cleaning & prep
│   ├── forecasting/             # Prophet model code
│   └── utils/                   # Helper functions
├── pipelines/
│   ├── adf/                     # Azure Data Factory templates
│   └── airflow/                 # Airflow DAG definitions
├── dashboards/
│   └── retail_forecast.pbix     # Power BI dashboard file
├── data/
│   ├── raw/                     # Raw Census data
│   ├── processed/               # Cleaned data
│   └── predictions/             # Forecast outputs
├── tests/                       # Unit tests
├── config/
│   └── config.yaml              # Configuration settings
└── requirements.txt             # Python dependencies
```

## Quick Start

### Prerequisites
- Python 3.9+
- Power BI Desktop
- Azure account (free tier) OR Docker (for Airflow)
- Census Bureau API key (free)

### Installation

```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/retail-sales-forecast.git
cd retail-sales-forecast

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up configuration
cp config/config.example.yaml config/config.yaml
# Edit config.yaml with your API keys
```

### Run the Pipeline

```bash
# Option 1: Run locally
python src/main.py

# Option 2: Use Airflow (Docker)
docker-compose up -d
# Access Airflow UI at http://localhost:8080

# Option 3: Deploy to Azure Data Factory
# See docs/04-ETL-PIPELINE.md for ADF setup
```

## Retail Category Focus

This project provides a **deep-dive analysis** of a single retail category:

**Food and Beverage Stores (NAICS 445)**
- Grocery stores
- Specialty food stores
- Beer, wine, and liquor stores

Why this category?
- Stable baseline with clear seasonal patterns
- Affected by holidays (Thanksgiving, Christmas)
- Demonstrates economic shock impact (inflation, supply chain)

## Dashboard Preview

The Power BI dashboard includes:

1. **Historical Trends** - Monthly sales with year-over-year comparison
2. **Forecast View** - Next 6 months prediction with 80%/95% confidence bands
3. **Seasonality Analysis** - Weekly and yearly patterns decomposition
4. **Anomaly Detection** - Flagged periods where actuals deviated from forecast
5. **Why Predictions Fail** - Analysis of forecast errors with explanations

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](docs/01-ARCHITECTURE.md) | System design and data flow |
| [Setup Guide](docs/02-SETUP.md) | Environment configuration |
| [Data Source](docs/03-DATA-SOURCE.md) | Census API details |
| [ETL Pipeline](docs/04-ETL-PIPELINE.md) | Pipeline setup (ADF/Airflow) |
| [Forecasting](docs/05-FORECASTING.md) | Prophet model implementation |
| [Dashboard](docs/06-DASHBOARD.md) | Power BI visualization guide |
| [Deployment](docs/07-DEPLOYMENT.md) | GitHub Pages hosting |

## Key Metrics

| Metric | Target | Description |
|--------|--------|-------------|
| MAPE | < 5% | Mean Absolute Percentage Error |
| Coverage | > 80% | % of actuals within confidence interval |
| Latency | < 5 min | End-to-end pipeline runtime |

## License

MIT License - See [LICENSE](LICENSE) for details.

## Author

**Alex** - Data Analyst Portfolio Project

---

*Part of the [alexdata.github.io](https://alexdata.github.io) portfolio*
