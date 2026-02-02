"""Export interactive Plotly charts for static hosting"""
import pandas as pd
import plotly.graph_objects as go
from pathlib import Path


def create_forecast_chart():
    """Main forecast chart with confidence bands"""
    df = pd.read_parquet("data/processed/retail_sales_clean.parquet")
    forecast = pd.read_csv("data/predictions/forecast_latest.csv")
    forecast['ds'] = pd.to_datetime(forecast['ds'])

    fig = go.Figure()

    # 95% confidence band
    fig.add_trace(go.Scatter(
        x=pd.concat([forecast['ds'], forecast['ds'][::-1]]),
        y=pd.concat([forecast['yhat_upper_95'], forecast['yhat_lower_95'][::-1]]),
        fill='toself',
        fillcolor='rgba(25,118,210,0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        name='95% Confidence',
        hoverinfo='skip'
    ))

    # 80% confidence band
    fig.add_trace(go.Scatter(
        x=pd.concat([forecast['ds'], forecast['ds'][::-1]]),
        y=pd.concat([forecast['yhat_upper_80'], forecast['yhat_lower_80'][::-1]]),
        fill='toself',
        fillcolor='rgba(25,118,210,0.2)',
        line=dict(color='rgba(255,255,255,0)'),
        name='80% Confidence',
        hoverinfo='skip'
    ))

    # Forecast line
    fig.add_trace(go.Scatter(
        x=forecast['ds'],
        y=forecast['yhat'],
        mode='lines',
        name='Forecast',
        line=dict(color='#1976D2', width=2)
    ))

    # Actual data points
    fig.add_trace(go.Scatter(
        x=df['ds'],
        y=df['y'],
        mode='markers',
        name='Actual',
        marker=dict(color='#212121', size=5)
    ))

    fig.update_layout(
        title='U.S. Retail Sales Forecast - Food & Beverage Stores',
        xaxis_title='Date',
        yaxis_title='Sales (Millions USD)',
        template='plotly_white',
        hovermode='x unified',
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        margin=dict(l=60, r=30, t=80, b=60)
    )

    return fig


def create_seasonality_chart():
    """Monthly seasonality pattern"""
    df = pd.read_parquet("data/processed/retail_sales_clean.parquet")

    monthly = df.groupby(df['ds'].dt.month)['y'].mean().reset_index()
    months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    monthly['month_name'] = monthly['ds'].apply(lambda x: months[x-1])

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=monthly['month_name'],
        y=monthly['y'],
        marker_color='#1976D2'
    ))

    fig.update_layout(
        title='Monthly Seasonality Pattern',
        xaxis_title='Month',
        yaxis_title='Average Sales (Millions USD)',
        template='plotly_white'
    )

    return fig


def create_yoy_chart():
    """Year-over-year comparison"""
    df = pd.read_parquet("data/processed/retail_sales_clean.parquet")
    df['year'] = df['ds'].dt.year
    df['month'] = df['ds'].dt.month

    # Last 3 years
    recent_years = sorted(df['year'].unique())[-3:]
    df_recent = df[df['year'].isin(recent_years)]

    fig = go.Figure()
    colors = ['#90CAF9', '#42A5F5', '#1976D2']

    for i, year in enumerate(recent_years):
        year_data = df_recent[df_recent['year'] == year]
        fig.add_trace(go.Scatter(
            x=year_data['month'],
            y=year_data['y'],
            mode='lines+markers',
            name=str(year),
            line=dict(color=colors[i], width=2)
        ))

    fig.update_layout(
        title='Year-over-Year Comparison',
        xaxis_title='Month',
        yaxis_title='Sales (Millions USD)',
        template='plotly_white',
        xaxis=dict(tickmode='array', tickvals=list(range(1,13)),
                   ticktext=['J','F','M','A','M','J','J','A','S','O','N','D'])
    )

    return fig


def export_all():
    output_dir = Path("static")
    output_dir.mkdir(exist_ok=True)

    charts = [
        ('forecast-chart.html', create_forecast_chart()),
        ('seasonality-chart.html', create_seasonality_chart()),
        ('yoy-chart.html', create_yoy_chart()),
    ]

    for filename, fig in charts:
        filepath = output_dir / filename
        fig.write_html(filepath, include_plotlyjs='cdn', full_html=True)
        print(f"Exported: {filepath}")

    # Also create combined dashboard
    combined = Path("static/dashboard.html")
    html = """<!DOCTYPE html>
<html>
<head>
    <title>Retail Sales Forecast Dashboard</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        h1 { color: #1976D2; }
        .chart { background: white; border-radius: 8px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        iframe { border: none; width: 100%; height: 450px; }
        .metrics { display: flex; gap: 20px; margin: 20px 0; }
        .metric { background: white; padding: 20px; border-radius: 8px; flex: 1; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .metric-value { font-size: 2em; font-weight: bold; color: #1976D2; }
        .metric-label { color: #666; margin-top: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>U.S. Retail Sales Forecast</h1>
        <p>Food & Beverage Stores (NAICS 445) | Data: U.S. Census Bureau</p>

        <div class="metrics">
            <div class="metric">
                <div class="metric-value" id="current">-</div>
                <div class="metric-label">Latest Month</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="forecast">-</div>
                <div class="metric-label">Next Month Forecast</div>
            </div>
            <div class="metric">
                <div class="metric-value" id="growth">-</div>
                <div class="metric-label">YoY Growth</div>
            </div>
        </div>

        <div class="chart">
            <iframe src="forecast-chart.html"></iframe>
        </div>

        <div class="chart">
            <iframe src="yoy-chart.html"></iframe>
        </div>

        <div class="chart">
            <iframe src="seasonality-chart.html"></iframe>
        </div>

        <p style="text-align:center; color:#666; margin-top:40px;">
            <a href="https://github.com/alexdata/retail-forecast">View Source Code</a> |
            Built with Python, Prophet, and Plotly
        </p>
    </div>
</body>
</html>"""
    combined.write_text(html)
    print(f"Exported: {combined}")


if __name__ == "__main__":
    export_all()
