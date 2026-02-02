"""Prophet forecasting model"""
import pickle
import pandas as pd
from pathlib import Path
from datetime import datetime
from prophet import Prophet
import warnings
warnings.filterwarnings('ignore')


class RetailForecaster:
    def __init__(self):
        self.model = None

    def _create_holidays(self) -> pd.DataFrame:
        holidays = []
        for year in range(2015, 2030):
            holidays.extend([
                {'holiday': 'thanksgiving', 'ds': pd.Timestamp(year, 11, 25), 'lower_window': -3, 'upper_window': 1},
                {'holiday': 'christmas', 'ds': pd.Timestamp(year, 12, 25), 'lower_window': -14, 'upper_window': 1},
                {'holiday': 'new_year', 'ds': pd.Timestamp(year, 1, 1), 'lower_window': -1, 'upper_window': 1},
            ])
        return pd.DataFrame(holidays)

    def train(self, df: pd.DataFrame):
        train_df = df[['ds', 'y']].copy()
        train_df = train_df.dropna()

        print(f"Training Prophet on {len(train_df)} observations...")

        self.model = Prophet(
            seasonality_mode='multiplicative',
            yearly_seasonality=True,
            weekly_seasonality=False,
            daily_seasonality=False,
            holidays=self._create_holidays(),
            interval_width=0.95
        )
        self.model.fit(train_df)
        print("Training complete.")

    def predict(self, periods: int = 6) -> pd.DataFrame:
        future = self.model.make_future_dataframe(periods=periods, freq='MS')
        forecast = self.model.predict(future)

        # Add 80% CI
        std = (forecast['yhat_upper'] - forecast['yhat_lower']) / (2 * 1.96)
        forecast['yhat_lower_80'] = forecast['yhat'] - 1.28 * std
        forecast['yhat_upper_80'] = forecast['yhat'] + 1.28 * std

        result = forecast[[
            'ds', 'yhat', 'yhat_lower', 'yhat_upper',
            'yhat_lower_80', 'yhat_upper_80', 'trend', 'yearly'
        ]].copy()
        result.columns = [
            'ds', 'yhat', 'yhat_lower_95', 'yhat_upper_95',
            'yhat_lower_80', 'yhat_upper_80', 'trend', 'yearly'
        ]
        return result

    def save_model(self, path: str = "models/prophet_model.pkl"):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'wb') as f:
            pickle.dump(self.model, f)
        print(f"Model saved to {path}")

    def save_forecast(self, forecast: pd.DataFrame, output_dir: str = "data/predictions"):
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Timestamped version
        timestamp = datetime.now().strftime("%Y%m%d")
        filepath = Path(output_dir) / f"forecast_{timestamp}.csv"
        forecast.to_csv(filepath, index=False)

        # Latest version (for Power BI)
        latest = Path(output_dir) / "forecast_latest.csv"
        forecast.to_csv(latest, index=False)

        print(f"Forecast saved to {filepath}")


if __name__ == "__main__":
    # Load data
    df = pd.read_parquet("data/processed/retail_sales_clean.parquet")

    # Train
    forecaster = RetailForecaster()
    forecaster.train(df)

    # Predict
    forecast = forecaster.predict(periods=6)

    # Show forecast
    print("\nForecast (next 6 months):")
    print(forecast[['ds', 'yhat', 'yhat_lower_95', 'yhat_upper_95']].tail(6).to_string(index=False))

    # Save
    forecaster.save_model()
    forecaster.save_forecast(forecast)
