# QUICKSTART - Get Running in 2 Hours

## Phase 1: Get Data (30 min)

### 1.1 Get Census API Key
```bash
# Open browser
open https://api.census.gov/data/key_signup.html
# Fill form, check email, copy key
```

### 1.2 Setup Environment
```bash
cd /Users/alex/Documents/0work/docker/00-porfolio/project_01_retail_forecast

# Create venv
python3 -m venv venv
source venv/bin/activate

# Install minimal deps
pip install pandas requests python-dotenv prophet plotly pyarrow

# Create .env
echo "CENSUS_API_KEY=your_key_here" > .env
```

### 1.3 Fetch Data
```bash
python src/ingestion/census_extractor.py
# Creates: data/raw/census_mrts_YYYYMMDD.json
```

---

## Phase 2: Process & Forecast (30 min)

```bash
# Clean data
python src/transformation/clean_data.py
# Creates: data/processed/retail_sales_clean.parquet

# Train model & forecast
python src/forecasting/prophet_model.py
# Creates: data/predictions/forecast_latest.csv
# Creates: models/prophet_model.pkl
```

---

## Phase 3: Azure + Power BI (45 min)

### 3.1 Upload to Azure Blob
```bash
# Login
az login

# Create resources (if not exists)
az group create --name rg-retail --location eastus
az storage account create --name stgretailforecast --resource-group rg-retail --sku Standard_LRS

# Get connection string
az storage account show-connection-string --name stgretailforecast --query connectionString -o tsv

# Create container
az storage container create --name data --account-name stgretailforecast

# Upload files
az storage blob upload --account-name stgretailforecast --container-name data --file data/processed/retail_sales_clean.parquet --name processed/retail_sales_clean.parquet
az storage blob upload --account-name stgretailforecast --container-name data --file data/predictions/forecast_latest.csv --name predictions/forecast_latest.csv
```

### 3.2 Connect Power BI
1. Open Power BI Desktop
2. Get Data → Azure → Azure Blob Storage
3. Enter: `stgretailforecast`
4. Navigate to files, load both
5. Build dashboard (see 06-DASHBOARD.md)
6. Publish → My Workspace
7. File → Publish to web → Get embed code

### 3.3 Embed on laurela.com
```html
<!-- While Azure active: show live Power BI -->
<iframe
  title="Retail Forecast"
  width="100%"
  height="600"
  src="https://app.powerbi.com/view?r=YOUR_EMBED_CODE"
  frameborder="0"
  allowFullScreen="true">
</iframe>
```

---

## Phase 4: Export Static Backup (15 min)

```bash
# Export Plotly charts
python scripts/export_charts.py
# Creates: static/forecast-chart.html

# Screenshot Power BI pages
# Save as: static/dashboard-1.png, static/dashboard-2.png
```

---

## When Azure Expires

Just swap the iframe for static content:

```html
<!-- After Azure expires: show static charts -->
<div id="dashboard">
  <iframe src="static/forecast-chart.html" width="100%" height="500"></iframe>
  <img src="static/dashboard-1.png" alt="Dashboard" width="100%">
</div>
```

Same URL, no broken links.
