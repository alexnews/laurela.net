#!/usr/bin/env python3
"""
Retail Sales Forecasting Pipeline - Main Entry Point

This script runs the complete pipeline:
1. Extract data from Census Bureau API
2. Clean and transform data
3. Train Prophet model
4. Generate forecasts
5. Export results

Usage:
    python src/main.py
    python src/main.py --config config/config.yaml
"""
import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from ingestion.census_extractor import CensusExtractor
from transformation.clean_data import DataCleaner
from transformation.feature_engineering import FeatureEngineer
from forecasting.prophet_model import RetailForecaster


def run_pipeline(config_path: str = None):
    """
    Run the complete forecasting pipeline.

    Args:
        config_path: Path to configuration file
    """
    print("=" * 60)
    print("RETAIL SALES FORECASTING PIPELINE")
    print("=" * 60)

    # Step 1: Extract
    print("\n[1/4] Extracting data from Census Bureau API...")
    try:
        extractor = CensusExtractor(category_code="445")
        df = extractor.fetch_data(start_year=2015)
        raw_path = extractor.save_raw(df)
        print(f"      Extracted {len(df)} records")
    except Exception as e:
        print(f"      ERROR: {e}")
        return False

    # Step 2: Clean
    print("\n[2/4] Cleaning and validating data...")
    try:
        cleaner = DataCleaner()
        df = cleaner.load_raw(raw_path)
        if not cleaner.validate(df):
            print(f"      Warnings: {cleaner.validation_errors}")
        df_clean = cleaner.clean(df)
        clean_path = cleaner.save_processed(df_clean)
        print(f"      Cleaned data saved")
    except Exception as e:
        print(f"      ERROR: {e}")
        return False

    # Step 3: Feature Engineering
    print("\n[3/4] Engineering features...")
    try:
        engineer = FeatureEngineer()
        df_features = engineer.add_time_features(df_clean)
        df_features = engineer.add_lag_features(df_features)
        df_features = engineer.add_covid_indicator(df_features)
        features_path = engineer.save_features(df_features)
        print(f"      Added {len(df_features.columns)} features")
    except Exception as e:
        print(f"      ERROR: {e}")
        return False

    # Step 4: Forecast
    print("\n[4/4] Training model and generating forecast...")
    try:
        forecaster = RetailForecaster()
        forecaster.train(df_features)

        # Evaluate
        metrics = forecaster.evaluate(df_features)
        print(f"      MAPE: {metrics['mape']:.2f}%")
        print(f"      Coverage: {metrics['coverage']:.2f}%")

        # Generate forecast
        forecast = forecaster.predict(periods=6)
        forecast_path = forecaster.save_forecast(forecast)
        model_path = forecaster.save_model()

        print(f"\n      Forecast for next 6 months:")
        print(forecast[['ds', 'yhat', 'yhat_lower_95', 'yhat_upper_95']].tail(6).to_string(index=False))
    except Exception as e:
        print(f"      ERROR: {e}")
        return False

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETED SUCCESSFULLY")
    print("=" * 60)
    print(f"\nOutputs:")
    print(f"  - Raw data:    {raw_path}")
    print(f"  - Clean data:  {clean_path}")
    print(f"  - Features:    {features_path}")
    print(f"  - Forecast:    {forecast_path}")
    print(f"  - Model:       {model_path}")

    return True


def main():
    parser = argparse.ArgumentParser(
        description="Retail Sales Forecasting Pipeline"
    )
    parser.add_argument(
        "--config",
        type=str,
        default="config/config.yaml",
        help="Path to configuration file"
    )
    args = parser.parse_args()

    success = run_pipeline(args.config)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
