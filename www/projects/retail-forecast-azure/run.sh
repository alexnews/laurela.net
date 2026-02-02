#!/bin/bash
# Run the complete retail forecast pipeline

set -e  # Exit on error

echo "=========================================="
echo "  RETAIL SALES FORECASTING PIPELINE"
echo "=========================================="

cd "$(dirname "$0")"

# Check for .env
if [ ! -f .env ]; then
    echo "ERROR: .env file not found"
    echo "Create .env with: CENSUS_API_KEY=your_key"
    exit 1
fi

# Activate venv if exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

echo ""
echo "[1/4] Extracting data from Census API..."
python src/ingestion/census_extractor.py

echo ""
echo "[2/4] Cleaning and transforming data..."
python src/transformation/clean_data.py

echo ""
echo "[3/4] Training Prophet model and forecasting..."
python src/forecasting/prophet_model.py

echo ""
echo "[4/4] Exporting charts for web..."
python scripts/export_charts.py

echo ""
echo "=========================================="
echo "  PIPELINE COMPLETE"
echo "=========================================="
echo ""
echo "Outputs:"
echo "  - data/raw/           Raw Census data"
echo "  - data/processed/     Cleaned Parquet"
echo "  - data/predictions/   Forecast CSV"
echo "  - models/             Prophet model"
echo "  - static/             Web charts"
echo ""
echo "Next steps:"
echo "  1. Upload data to Azure Blob"
echo "  2. Connect Power BI to Azure"
echo "  3. Get embed code"
echo "  4. Update web/index.html with embed code"
echo "  5. Deploy web/ folder to laurela.com/projects/retail-forecast/"
