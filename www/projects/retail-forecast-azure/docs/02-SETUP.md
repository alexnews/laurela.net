# Environment Setup Guide

This guide walks you through setting up all required tools and accounts.

## Prerequisites Checklist

- [ ] Python 3.9 or higher
- [ ] Git
- [ ] Power BI Desktop (Windows) or Power BI Service account
- [ ] Census Bureau API key
- [ ] Azure account (free tier) OR Docker Desktop

## Step 1: Python Environment

### 1.1 Install Python

**macOS:**
```bash
# Using Homebrew
brew install python@3.11

# Verify installation
python3 --version
```

**Windows:**
```bash
# Download from python.org or use winget
winget install Python.Python.3.11

# Verify installation
python --version
```

### 1.2 Create Virtual Environment

```bash
# Navigate to project directory
cd project_01_retail_forecast

# Create virtual environment
python -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate

# Verify activation (should show venv path)
which python  # macOS/Linux
where python  # Windows
```

### 1.3 Install Dependencies

Create `requirements.txt`:

```txt
# Core data processing
pandas>=2.0.0
numpy>=1.24.0
pyarrow>=14.0.0

# API and web requests
requests>=2.31.0
python-dotenv>=1.0.0

# Forecasting
prophet>=1.1.5

# Data validation
pydantic>=2.0.0

# Visualization (optional, for local testing)
plotly>=5.18.0
matplotlib>=3.8.0

# Testing
pytest>=7.4.0

# Azure SDK (if using ADF)
azure-storage-blob>=12.19.0
azure-identity>=1.15.0

# Airflow (if using local orchestration)
apache-airflow>=2.8.0
```

Install all dependencies:

```bash
pip install -r requirements.txt
```

### 1.4 Prophet Installation Notes

Prophet has specific dependencies. If installation fails:

**macOS:**
```bash
# Install cmdstan (required by Prophet)
brew install cmdstan

# Then install Prophet
pip install prophet
```

**Windows:**
```bash
# Install Visual C++ Build Tools first
# Download from: https://visualstudio.microsoft.com/visual-cpp-build-tools/

# Then install Prophet
pip install prophet
```

**Alternative - Use Conda:**
```bash
conda install -c conda-forge prophet
```

## Step 2: Census Bureau API Key

### 2.1 Register for API Key

1. Go to: https://api.census.gov/data/key_signup.html
2. Fill out the form:
   - Organization: Personal/Portfolio Project
   - Email: your email
   - Agree to terms
3. Check your email for the API key (arrives within minutes)

### 2.2 Store API Key Securely

Create `.env` file in project root:

```bash
# .env
CENSUS_API_KEY=your_api_key_here
```

**IMPORTANT:** Add `.env` to `.gitignore`:

```bash
echo ".env" >> .gitignore
```

### 2.3 Test API Access

```python
# test_census_api.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("CENSUS_API_KEY")
BASE_URL = "https://api.census.gov/data/timeseries/eits/mrts"

# Test request - get latest retail sales for Food & Beverage
params = {
    "get": "cell_value,time_slot_id,category_code",
    "category_code": "445",  # Food and Beverage Stores
    "data_type_code": "SM",  # Monthly Sales
    "time_slot_id": "from 2020",
    "key": API_KEY
}

response = requests.get(BASE_URL, params=params)

if response.status_code == 200:
    print("API connection successful!")
    print(f"Sample data: {response.json()[:3]}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
```

Run the test:
```bash
python test_census_api.py
```

## Step 3: Azure Setup (Option A)

### 3.1 Create Azure Free Account

1. Go to: https://azure.microsoft.com/free/
2. Sign up with Microsoft account
3. You get $200 credit for 30 days

### 3.2 Create Resource Group

```bash
# Install Azure CLI
# macOS:
brew install azure-cli

# Windows:
winget install Microsoft.AzureCLI

# Login to Azure
az login

# Create resource group
az group create \
  --name rg-retail-forecast \
  --location eastus
```

### 3.3 Create Storage Account

```bash
# Create storage account (name must be globally unique)
az storage account create \
  --name stgretailforecast$(date +%s) \
  --resource-group rg-retail-forecast \
  --location eastus \
  --sku Standard_LRS

# Create containers
az storage container create --name raw --account-name <storage_account_name>
az storage container create --name processed --account-name <storage_account_name>
az storage container create --name predictions --account-name <storage_account_name>
```

### 3.4 Create Azure Data Factory

```bash
# Create Data Factory
az datafactory create \
  --resource-group rg-retail-forecast \
  --factory-name adf-retail-forecast \
  --location eastus
```

### 3.5 Store Azure Credentials

Add to `.env`:

```bash
# Azure credentials
AZURE_STORAGE_ACCOUNT=stgretailforecast123456
AZURE_STORAGE_KEY=your_storage_key_here
AZURE_SUBSCRIPTION_ID=your_subscription_id
```

Get storage key:
```bash
az storage account keys list \
  --account-name <storage_account_name> \
  --resource-group rg-retail-forecast \
  --query "[0].value" -o tsv
```

## Step 4: Airflow Setup (Option B)

### 4.1 Install Docker Desktop

Download from: https://www.docker.com/products/docker-desktop/

Verify installation:
```bash
docker --version
docker-compose --version
```

### 4.2 Create Docker Compose File

Create `docker-compose.yaml`:

```yaml
version: '3.8'

x-airflow-common:
  &airflow-common
  image: apache/airflow:2.8.0-python3.11
  environment:
    &airflow-common-env
    AIRFLOW__CORE__EXECUTOR: LocalExecutor
    AIRFLOW__DATABASE__SQL_ALCHEMY_CONN: postgresql+psycopg2://airflow:airflow@postgres/airflow
    AIRFLOW__CORE__FERNET_KEY: ''
    AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION: 'true'
    AIRFLOW__CORE__LOAD_EXAMPLES: 'false'
    AIRFLOW__API__AUTH_BACKENDS: 'airflow.api.auth.backend.basic_auth'
    CENSUS_API_KEY: ${CENSUS_API_KEY}
  volumes:
    - ./dags:/opt/airflow/dags
    - ./logs:/opt/airflow/logs
    - ./plugins:/opt/airflow/plugins
    - ./data:/opt/airflow/data
    - ./src:/opt/airflow/src
  user: "${AIRFLOW_UID:-50000}:0"
  depends_on:
    postgres:
      condition: service_healthy

services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    volumes:
      - postgres-db-volume:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD", "pg_isready", "-U", "airflow"]
      interval: 5s
      retries: 5

  airflow-webserver:
    <<: *airflow-common
    command: webserver
    ports:
      - 8080:8080
    healthcheck:
      test: ["CMD", "curl", "--fail", "http://localhost:8080/health"]
      interval: 10s
      timeout: 10s
      retries: 5

  airflow-scheduler:
    <<: *airflow-common
    command: scheduler
    healthcheck:
      test: ["CMD-SHELL", "airflow jobs check --job-type SchedulerJob --hostname $(hostname)"]
      interval: 10s
      timeout: 10s
      retries: 5

  airflow-init:
    <<: *airflow-common
    entrypoint: /bin/bash
    command:
      - -c
      - |
        airflow db init
        airflow users create \
          --username admin \
          --firstname Admin \
          --lastname User \
          --role Admin \
          --email admin@example.com \
          --password admin

volumes:
  postgres-db-volume:
```

### 4.3 Initialize Airflow

```bash
# Create required directories
mkdir -p dags logs plugins data/raw data/processed data/predictions

# Set Airflow UID (Linux/macOS)
echo -e "AIRFLOW_UID=$(id -u)" > .env.airflow

# Start services
docker-compose up -d

# Wait for initialization (first time takes a few minutes)
docker-compose logs -f airflow-init

# Access Airflow UI
open http://localhost:8080
# Login: admin / admin
```

### 4.4 Install Python Packages in Airflow

Create `requirements-airflow.txt` for Airflow container:

```txt
prophet>=1.1.5
pandas>=2.0.0
pyarrow>=14.0.0
requests>=2.31.0
python-dotenv>=1.0.0
```

Update docker-compose.yaml to install packages:

```yaml
x-airflow-common:
  &airflow-common
  build:
    context: .
    dockerfile: Dockerfile.airflow
```

Create `Dockerfile.airflow`:

```dockerfile
FROM apache/airflow:2.8.0-python3.11

COPY requirements-airflow.txt /requirements-airflow.txt
RUN pip install --no-cache-dir -r /requirements-airflow.txt
```

Rebuild:
```bash
docker-compose build
docker-compose up -d
```

## Step 5: Power BI Setup

### 5.1 Install Power BI Desktop (Windows)

Download from: https://powerbi.microsoft.com/desktop/

Or via Microsoft Store.

### 5.2 Power BI on macOS

Power BI Desktop is Windows-only. Options for macOS:

1. **Power BI Service (Web):** https://app.powerbi.com
   - Free account available
   - Limited compared to Desktop

2. **Parallels/VMware:** Run Windows VM

3. **Alternative:** Use Plotly/Dash for Python-native dashboards

### 5.3 Configure Data Source

In Power BI Desktop:
1. Get Data > Text/CSV or Parquet
2. Navigate to `data/processed/` folder
3. Select data files
4. Transform data as needed

## Step 6: Project Configuration

### 6.1 Create Config File

Create `config/config.yaml`:

```yaml
# Project configuration
project:
  name: retail-sales-forecast
  version: 1.0.0

# Data source settings
census_api:
  base_url: https://api.census.gov/data/timeseries/eits/mrts
  category_code: "445"  # Food and Beverage Stores
  data_type_code: "SM"  # Monthly Sales
  start_year: 2015

# Data paths
paths:
  raw: data/raw
  processed: data/processed
  predictions: data/predictions
  models: models

# Prophet model settings
prophet:
  seasonality_mode: multiplicative
  yearly_seasonality: true
  weekly_seasonality: false
  changepoint_prior_scale: 0.05
  interval_width: 0.95
  forecast_periods: 6  # months ahead

# Dashboard settings
dashboard:
  confidence_levels: [0.80, 0.95]
  export_format: png
```

### 6.2 Create Example Config

```bash
cp config/config.yaml config/config.example.yaml
```

Add to `.gitignore`:
```bash
echo "config/config.yaml" >> .gitignore
```

## Step 7: Verify Setup

Run the setup verification script:

```python
# verify_setup.py
import sys
import os

def check_python_version():
    version = sys.version_info
    assert version.major == 3 and version.minor >= 9, "Python 3.9+ required"
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")

def check_dependencies():
    required = ['pandas', 'numpy', 'prophet', 'requests', 'pyarrow']
    for pkg in required:
        try:
            __import__(pkg)
            print(f"{pkg}: installed")
        except ImportError:
            print(f"{pkg}: MISSING")

def check_env_variables():
    required_vars = ['CENSUS_API_KEY']
    from dotenv import load_dotenv
    load_dotenv()

    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"{var}: configured")
        else:
            print(f"{var}: MISSING")

def check_directories():
    dirs = ['data/raw', 'data/processed', 'data/predictions', 'models', 'config']
    for d in dirs:
        if os.path.exists(d):
            print(f"{d}/: exists")
        else:
            os.makedirs(d, exist_ok=True)
            print(f"{d}/: created")

if __name__ == "__main__":
    print("=== Setup Verification ===\n")

    print("1. Python Version:")
    check_python_version()

    print("\n2. Dependencies:")
    check_dependencies()

    print("\n3. Environment Variables:")
    check_env_variables()

    print("\n4. Directories:")
    check_directories()

    print("\n=== Verification Complete ===")
```

Run:
```bash
python verify_setup.py
```

## Troubleshooting

### Prophet Installation Fails

```bash
# Try conda instead
conda create -n retail-forecast python=3.11
conda activate retail-forecast
conda install -c conda-forge prophet pandas pyarrow
```

### Docker Permission Errors

```bash
# Add user to docker group (Linux)
sudo usermod -aG docker $USER
# Log out and back in
```

### Azure CLI Login Issues

```bash
# Clear cached credentials
az logout
az account clear
az login
```

## Next Steps

1. [Configure Census data source](03-DATA-SOURCE.md)
2. [Build the ETL pipeline](04-ETL-PIPELINE.md)
