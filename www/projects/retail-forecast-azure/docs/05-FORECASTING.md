# Prophet Forecasting Model

This document covers implementing the Facebook Prophet forecasting model for retail sales prediction.

## Why Prophet?

Prophet is ideal for this project because:

1. **Handles seasonality automatically** - Detects yearly, weekly patterns
2. **Robust to missing data** - Common in government data
3. **Handles outliers** - COVID-19 impact won't break the model
4. **Interpretable** - Can explain trend, seasonality, holidays separately
5. **Confidence intervals** - Built-in uncertainty quantification

## Model Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    PROPHET MODEL                         │
├─────────────────────────────────────────────────────────┤
│                                                          │
│   y(t) = g(t) + s(t) + h(t) + ε(t)                      │
│                                                          │
│   Where:                                                 │
│   ├── g(t) = Trend (growth over time)                   │
│   ├── s(t) = Seasonality (yearly patterns)              │
│   ├── h(t) = Holiday effects                            │
│   └── ε(t) = Error term                                 │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

## Implementation

### File: `src/forecasting/prophet_model.py`

```python
"""
Prophet Forecasting Model for Retail Sales
"""
import os
import json
import pickle
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics
import warnings
warnings.filterwarnings('ignore')


class RetailForecaster:
    """
    Prophet-based forecasting for retail sales.
    """

    def __init__(self, config: dict = None):
        """
        Initialize forecaster with configuration.

        Args:
            config: Model configuration dictionary
        """
        self.config = config or self._default_config()
        self.model = None
        self.metrics = {}

    def _default_config(self) -> dict:
        """Default Prophet configuration."""
        return {
            'seasonality_mode': 'multiplicative',  # Better for retail
            'yearly_seasonality': True,
            'weekly_seasonality': False,  # Monthly data
            'daily_seasonality': False,
            'changepoint_prior_scale': 0.05,  # Flexibility of trend
            'seasonality_prior_scale': 10,
            'holidays_prior_scale': 10,
            'interval_width': 0.95,  # Confidence interval
            'forecast_periods': 6,  # Months ahead
        }

    def _create_holidays(self) -> pd.DataFrame:
        """
        Create holiday dataframe for Prophet.

        Returns:
            DataFrame with holiday definitions
        """
        holidays = []

        for year in range(2015, 2030):
            # Thanksgiving (4th Thursday of November)
            nov_first = pd.Timestamp(year, 11, 1)
            thanksgiving = nov_first + pd.offsets.Week(weekday=3)
            while thanksgiving.month != 11 or thanksgiving.day < 22:
                thanksgiving += pd.offsets.Week(1)

            holidays.extend([
                {
                    'holiday': 'thanksgiving_week',
                    'ds': thanksgiving,
                    'lower_window': -2,
                    'upper_window': 4,  # Black Friday weekend
                },
                {
                    'holiday': 'christmas_season',
                    'ds': pd.Timestamp(year, 12, 25),
                    'lower_window': -14,  # 2 weeks before
                    'upper_window': 7,    # Through New Year
                },
                {
                    'holiday': 'new_year',
                    'ds': pd.Timestamp(year, 1, 1),
                    'lower_window': -1,
                    'upper_window': 1,
                },
                {
                    'holiday': 'easter_season',
                    'ds': pd.Timestamp(year, 4, 15),  # Approximate
                    'lower_window': -7,
                    'upper_window': 0,
                },
                {
                    'holiday': 'july_4th',
                    'ds': pd.Timestamp(year, 7, 4),
                    'lower_window': -3,
                    'upper_window': 1,
                },
            ])

        return pd.DataFrame(holidays)

    def _add_regressors(self, model: Prophet) -> Prophet:
        """
        Add custom regressors to the model.

        Can add external factors like:
        - COVID impact
        - Economic indicators
        - Price indices
        """
        # COVID impact periods (can be added to training data)
        # model.add_regressor('covid_lockdown')
        # model.add_regressor('covid_recovery')

        return model

    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepare data for Prophet.

        Prophet requires:
        - 'ds': datetime column
        - 'y': target column

        Args:
            df: Input dataframe

        Returns:
            Prepared dataframe
        """
        prophet_df = df[['ds', 'y']].copy()

        # Ensure datetime
        prophet_df['ds'] = pd.to_datetime(prophet_df['ds'])

        # Remove any nulls
        prophet_df = prophet_df.dropna()

        # Sort by date
        prophet_df = prophet_df.sort_values('ds').reset_index(drop=True)

        return prophet_df

    def train(self, df: pd.DataFrame) -> 'RetailForecaster':
        """
        Train the Prophet model.

        Args:
            df: Training data with 'ds' and 'y' columns

        Returns:
            self (for method chaining)
        """
        # Prepare data
        train_df = self.prepare_data(df)

        # Initialize Prophet with configuration
        self.model = Prophet(
            seasonality_mode=self.config['seasonality_mode'],
            yearly_seasonality=self.config['yearly_seasonality'],
            weekly_seasonality=self.config['weekly_seasonality'],
            daily_seasonality=self.config['daily_seasonality'],
            changepoint_prior_scale=self.config['changepoint_prior_scale'],
            seasonality_prior_scale=self.config['seasonality_prior_scale'],
            holidays_prior_scale=self.config['holidays_prior_scale'],
            interval_width=self.config['interval_width'],
            holidays=self._create_holidays(),
        )

        # Add custom regressors
        self.model = self._add_regressors(self.model)

        # Fit the model
        print(f"Training Prophet model on {len(train_df)} observations...")
        self.model.fit(train_df)
        print("Training complete.")

        return self

    def predict(self, periods: int = None) -> pd.DataFrame:
        """
        Generate forecast.

        Args:
            periods: Number of periods to forecast (default from config)

        Returns:
            DataFrame with predictions and confidence intervals
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        periods = periods or self.config['forecast_periods']

        # Create future dataframe
        future = self.model.make_future_dataframe(
            periods=periods,
            freq='MS'  # Month Start
        )

        # Generate predictions
        forecast = self.model.predict(future)

        # Select relevant columns
        result = forecast[[
            'ds',
            'yhat',
            'yhat_lower',
            'yhat_upper',
            'trend',
            'yearly',
        ]].copy()

        # Add 80% confidence interval
        # Prophet uses interval_width for the default interval
        # Calculate 80% manually
        std = (forecast['yhat_upper'] - forecast['yhat_lower']) / (2 * 1.96)
        result['yhat_lower_80'] = forecast['yhat'] - 1.28 * std
        result['yhat_upper_80'] = forecast['yhat'] + 1.28 * std

        # Rename for clarity
        result = result.rename(columns={
            'yhat_lower': 'yhat_lower_95',
            'yhat_upper': 'yhat_upper_95',
        })

        return result

    def evaluate(self, df: pd.DataFrame, initial: str = '730 days',
                 period: str = '30 days', horizon: str = '90 days') -> dict:
        """
        Evaluate model using cross-validation.

        Args:
            df: Full dataset
            initial: Initial training period
            period: Spacing between cutoff dates
            horizon: Forecast horizon

        Returns:
            Dictionary of performance metrics
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        print("Running cross-validation...")
        cv_results = cross_validation(
            self.model,
            initial=initial,
            period=period,
            horizon=horizon
        )

        # Calculate performance metrics
        metrics_df = performance_metrics(cv_results)

        self.metrics = {
            'mape': metrics_df['mape'].mean() * 100,  # Percentage
            'rmse': metrics_df['rmse'].mean(),
            'mae': metrics_df['mae'].mean(),
            'coverage': metrics_df['coverage'].mean() * 100,  # Percentage
        }

        print(f"MAPE: {self.metrics['mape']:.2f}%")
        print(f"RMSE: {self.metrics['rmse']:.2f}")
        print(f"MAE: {self.metrics['mae']:.2f}")
        print(f"Coverage: {self.metrics['coverage']:.2f}%")

        return self.metrics

    def get_components(self) -> dict:
        """
        Extract model components for analysis.

        Returns:
            Dictionary with trend, seasonality breakdowns
        """
        if self.model is None:
            raise ValueError("Model not trained. Call train() first.")

        # Get the training data range
        history = self.model.history

        # Predict on training data to get components
        components = self.model.predict(history)

        return {
            'trend': components[['ds', 'trend']],
            'yearly': components[['ds', 'yearly']],
            'holidays': components[['ds', 'holidays']] if 'holidays' in components else None,
        }

    def explain_forecast_error(self, actual: pd.DataFrame,
                                forecast: pd.DataFrame) -> pd.DataFrame:
        """
        Analyze why forecasts differ from actuals.

        This is the KEY DIFFERENTIATOR of this project.

        Args:
            actual: DataFrame with 'ds' and 'y' columns
            forecast: DataFrame with predictions

        Returns:
            DataFrame with error analysis
        """
        # Merge actual and forecast
        merged = pd.merge(actual, forecast, on='ds', how='inner')
        merged['error'] = merged['y'] - merged['yhat']
        merged['abs_error'] = abs(merged['error'])
        merged['pct_error'] = merged['error'] / merged['y'] * 100

        # Classify errors
        merged['error_category'] = 'Normal'

        # Check if in holiday period
        holidays = self._create_holidays()
        for _, holiday in holidays.iterrows():
            mask = (
                (merged['ds'] >= holiday['ds'] + pd.Timedelta(days=holiday['lower_window'])) &
                (merged['ds'] <= holiday['ds'] + pd.Timedelta(days=holiday['upper_window']))
            )
            merged.loc[mask & (merged['abs_error'] > merged['abs_error'].std()), 'error_category'] = 'Holiday Effect'

        # COVID period
        covid_mask = (merged['ds'] >= '2020-03-01') & (merged['ds'] <= '2021-06-01')
        merged.loc[covid_mask & (merged['abs_error'] > merged['abs_error'].std()), 'error_category'] = 'COVID Impact'

        # Trend change
        merged['trend_change'] = merged['trend'].diff().abs()
        merged.loc[merged['trend_change'] > merged['trend_change'].quantile(0.9), 'error_category'] = 'Trend Shift'

        # Generate explanations
        merged['explanation'] = merged.apply(self._generate_explanation, axis=1)

        return merged[['ds', 'y', 'yhat', 'error', 'pct_error', 'error_category', 'explanation']]

    def _generate_explanation(self, row: pd.Series) -> str:
        """Generate human-readable explanation for forecast error."""
        if row['error_category'] == 'Holiday Effect':
            if row['error'] > 0:
                return "Actual exceeded forecast due to stronger-than-expected holiday demand"
            else:
                return "Holiday sales were weaker than historical patterns suggested"

        elif row['error_category'] == 'COVID Impact':
            if row['error'] > 0:
                return "Pandemic-related surge in grocery demand (stockpiling, home cooking)"
            else:
                return "Pandemic-related disruption reduced sales unexpectedly"

        elif row['error_category'] == 'Trend Shift':
            return "Structural change in consumer behavior or market conditions"

        else:
            if abs(row['pct_error']) < 5:
                return "Forecast within normal variance"
            elif row['error'] > 0:
                return "Unexplained positive variance - investigate promotions or new store openings"
            else:
                return "Unexplained negative variance - investigate competition or supply issues"

    def save_model(self, path: str = "models/prophet_model.pkl") -> str:
        """Save trained model to disk."""
        Path(path).parent.mkdir(parents=True, exist_ok=True)

        with open(path, 'wb') as f:
            pickle.dump(self.model, f)

        print(f"Model saved to {path}")
        return path

    def load_model(self, path: str = "models/prophet_model.pkl") -> 'RetailForecaster':
        """Load model from disk."""
        with open(path, 'rb') as f:
            self.model = pickle.load(f)

        print(f"Model loaded from {path}")
        return self

    def save_forecast(self, forecast: pd.DataFrame,
                      path: str = "data/predictions") -> str:
        """Save forecast results."""
        Path(path).mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d")
        filepath = Path(path) / f"forecast_{timestamp}.csv"

        forecast.to_csv(filepath, index=False)

        # Also save as latest
        latest_path = Path(path) / "forecast_latest.csv"
        forecast.to_csv(latest_path, index=False)

        print(f"Forecast saved to {filepath}")
        return str(filepath)


def train_and_forecast(**context):
    """
    Airflow callable function for training and forecasting.
    """
    ti = context['ti']
    features_path = ti.xcom_pull(key='features_file_path', task_ids='engineer_features')

    # Load data
    df = pd.read_parquet(features_path)

    # Initialize and train
    forecaster = RetailForecaster()
    forecaster.train(df)

    # Evaluate
    metrics = forecaster.evaluate(df)

    # Generate forecast
    forecast = forecaster.predict(periods=6)

    # Save outputs
    model_path = forecaster.save_model()
    forecast_path = forecaster.save_forecast(forecast)

    # Push to XCom
    ti.xcom_push(key='model_path', value=model_path)
    ti.xcom_push(key='forecast_path', value=forecast_path)
    ti.xcom_push(key='metrics', value=metrics)

    return forecast_path


# Standalone execution
if __name__ == "__main__":
    # Load sample data
    df = pd.read_parquet("data/processed/retail_sales_clean.parquet")

    # Train model
    forecaster = RetailForecaster()
    forecaster.train(df)

    # Evaluate
    metrics = forecaster.evaluate(df)

    # Generate forecast
    forecast = forecaster.predict(periods=6)
    print("\nForecast:")
    print(forecast.tail(6))

    # Explain errors (if we have actual data to compare)
    if len(forecast) > 6:
        analysis = forecaster.explain_forecast_error(df, forecast)
        print("\nError Analysis:")
        print(analysis[analysis['error_category'] != 'Normal'])

    # Save
    forecaster.save_model()
    forecaster.save_forecast(forecast)
```

## Model Configuration

### Configuration Options

| Parameter | Default | Description |
|-----------|---------|-------------|
| `seasonality_mode` | multiplicative | How seasonality combines with trend |
| `yearly_seasonality` | True | Enable yearly patterns |
| `weekly_seasonality` | False | Disabled for monthly data |
| `changepoint_prior_scale` | 0.05 | Trend flexibility (higher = more flexible) |
| `seasonality_prior_scale` | 10 | Seasonality strength |
| `holidays_prior_scale` | 10 | Holiday effect strength |
| `interval_width` | 0.95 | Confidence interval width |
| `forecast_periods` | 6 | Months to forecast |

### Tuning Guidelines

**For more flexible trend:**
```python
config = {'changepoint_prior_scale': 0.1}  # More responsive to changes
```

**For stronger seasonality:**
```python
config = {'seasonality_prior_scale': 15}  # Amplify seasonal patterns
```

**For wider confidence intervals:**
```python
config = {'interval_width': 0.99}  # 99% confidence
```

## Model Evaluation

### Metrics Explained

| Metric | Target | Interpretation |
|--------|--------|----------------|
| MAPE | < 5% | Mean Absolute Percentage Error |
| RMSE | Context-dependent | Root Mean Square Error (in sales units) |
| MAE | Context-dependent | Mean Absolute Error (in sales units) |
| Coverage | > 80% | % of actuals within confidence interval |

### Cross-Validation

```python
# Prophet uses rolling origin cross-validation
#
# |-------- initial --------|-- horizon --|
# |========================|xxxxxxxxxxxxx|
#                |-- period --|
#                |========================|xxxxxxxxxxxxx|
#                              |-- period --|
#                              |========================|xxxxxxxxxxxxx|
```

## Visualization

### Plot Forecast

```python
from prophet.plot import plot_plotly, plot_components_plotly

# Interactive forecast plot
fig = plot_plotly(forecaster.model, forecast)
fig.write_html("data/predictions/forecast_plot.html")

# Component breakdown
fig_components = plot_components_plotly(forecaster.model, forecast)
fig_components.write_html("data/predictions/components_plot.html")
```

### Custom Visualization

```python
import plotly.graph_objects as go

def create_forecast_chart(forecast: pd.DataFrame, actual: pd.DataFrame = None):
    """Create interactive forecast chart."""
    fig = go.Figure()

    # Confidence bands (95%)
    fig.add_trace(go.Scatter(
        x=forecast['ds'].tolist() + forecast['ds'].tolist()[::-1],
        y=forecast['yhat_upper_95'].tolist() + forecast['yhat_lower_95'].tolist()[::-1],
        fill='toself',
        fillcolor='rgba(0,100,255,0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        name='95% Confidence'
    ))

    # Confidence bands (80%)
    fig.add_trace(go.Scatter(
        x=forecast['ds'].tolist() + forecast['ds'].tolist()[::-1],
        y=forecast['yhat_upper_80'].tolist() + forecast['yhat_lower_80'].tolist()[::-1],
        fill='toself',
        fillcolor='rgba(0,100,255,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='80% Confidence'
    ))

    # Forecast line
    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat'],
        mode='lines',
        name='Forecast',
        line=dict(color='blue', width=2)
    ))

    # Actual values (if provided)
    if actual is not None:
        fig.add_trace(go.Scatter(
            x=actual['ds'],
            y=actual['y'],
            mode='markers',
            name='Actual',
            marker=dict(color='black', size=6)
        ))

    fig.update_layout(
        title='Retail Sales Forecast - Food & Beverage Stores',
        xaxis_title='Date',
        yaxis_title='Sales (Millions USD)',
        hovermode='x unified',
        template='plotly_white'
    )

    return fig
```

## Error Analysis (Key Differentiator)

The `explain_forecast_error` method categorizes and explains prediction errors:

### Error Categories

| Category | Detection Logic | Example Explanation |
|----------|-----------------|---------------------|
| Holiday Effect | Error during holiday window | "Stronger-than-expected holiday demand" |
| COVID Impact | Error during Mar 2020 - Jun 2021 | "Pandemic-related surge in grocery demand" |
| Trend Shift | Large change in trend component | "Structural change in consumer behavior" |
| Normal | Small error, no special conditions | "Forecast within normal variance" |

### Sample Output

```
ds          actual    forecast   error    category        explanation
2020-03-01  85234     72000      +13234   COVID Impact    Pandemic-related surge...
2020-11-01  92156     88000      +4156    Holiday Effect  Stronger-than-expected...
2022-06-01  71234     74500      -3266    Trend Shift     Structural change in...
```

## Next Steps

1. [Build Power BI dashboard](06-DASHBOARD.md)
2. [Deploy to GitHub Pages](07-DEPLOYMENT.md)
