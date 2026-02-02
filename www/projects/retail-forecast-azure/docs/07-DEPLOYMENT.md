# GitHub Pages Deployment

This document covers deploying your portfolio project to GitHub Pages.

## Overview

GitHub Pages provides free static hosting. Since Power BI dashboards can't run directly on static hosting, we'll use a combination of:

1. **Static HTML** - Project description and navigation
2. **Embedded charts** - Interactive Plotly charts exported as HTML
3. **Dashboard screenshots** - PNG images of Power BI dashboards
4. **PDF report** - Downloadable analysis document

## Project Portfolio Structure

```
alexdata.github.io/
├── index.html                    # Main portfolio page
├── projects/
│   └── retail-forecast/
│       ├── index.html            # Project landing page
│       ├── dashboard.html        # Interactive Plotly charts
│       ├── report.pdf            # Analysis document
│       └── assets/
│           ├── dashboard-1.png   # Power BI screenshots
│           ├── dashboard-2.png
│           ├── forecast-chart.html  # Plotly export
│           └── style.css
├── about.html
└── contact.html
```

## Step 1: Create GitHub Repository

### Option A: Username Repository (Recommended for main portfolio)

```bash
# Create repository named: username.github.io
# Example: alexdata.github.io

# Clone locally
git clone https://github.com/alexdata/alexdata.github.io.git
cd alexdata.github.io
```

### Option B: Project Repository

```bash
# Create regular repository
git clone https://github.com/alexdata/retail-sales-forecast.git
cd retail-sales-forecast

# Site will be at: alexdata.github.io/retail-sales-forecast
```

## Step 2: Create Main Portfolio Page

**`index.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Alex | Data Analyst Portfolio</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        :root {
            --primary: #1976D2;
            --secondary: #64B5F6;
            --dark: #212121;
            --light: #FAFAFA;
        }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background-color: var(--light);
            color: var(--dark);
        }
        .hero {
            background: linear-gradient(135deg, var(--primary), var(--secondary));
            color: white;
            padding: 80px 0;
        }
        .project-card {
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .project-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.15);
        }
        .tech-badge {
            background: var(--secondary);
            color: var(--dark);
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            margin: 2px;
            display: inline-block;
        }
    </style>
</head>
<body>
    <!-- Navigation -->
    <nav class="navbar navbar-expand-lg navbar-light bg-white shadow-sm">
        <div class="container">
            <a class="navbar-brand fw-bold" href="#">Alex Data</a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav ms-auto">
                    <li class="nav-item"><a class="nav-link" href="#projects">Projects</a></li>
                    <li class="nav-item"><a class="nav-link" href="#skills">Skills</a></li>
                    <li class="nav-item"><a class="nav-link" href="#about">About</a></li>
                    <li class="nav-item"><a class="nav-link" href="#contact">Contact</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <!-- Hero Section -->
    <section class="hero text-center">
        <div class="container">
            <h1 class="display-4 fw-bold">Alex</h1>
            <p class="lead">Data Analyst | Business Intelligence | Forecasting</p>
            <p class="mt-4">
                Transforming data into actionable insights using Python, SQL, and Power BI.
            </p>
            <a href="#projects" class="btn btn-light btn-lg mt-3">View Projects</a>
        </div>
    </section>

    <!-- Projects Section -->
    <section id="projects" class="py-5">
        <div class="container">
            <h2 class="text-center mb-5">Featured Projects</h2>
            <div class="row">
                <!-- Project 1: Retail Forecast -->
                <div class="col-lg-6 mb-4">
                    <div class="card project-card h-100">
                        <img src="projects/retail-forecast/assets/dashboard-1.png"
                             class="card-img-top" alt="Retail Forecast Dashboard">
                        <div class="card-body">
                            <h5 class="card-title">Retail Sales Forecasting System</h5>
                            <p class="card-text">
                                End-to-end forecasting pipeline using U.S. Census data.
                                Predicts monthly retail sales with confidence intervals
                                and explains why predictions fail.
                            </p>
                            <div class="mb-3">
                                <span class="tech-badge">Python</span>
                                <span class="tech-badge">Prophet</span>
                                <span class="tech-badge">Power BI</span>
                                <span class="tech-badge">Airflow</span>
                            </div>
                            <a href="projects/retail-forecast/" class="btn btn-primary">View Project</a>
                            <a href="https://github.com/alexdata/retail-sales-forecast"
                               class="btn btn-outline-secondary" target="_blank">GitHub</a>
                        </div>
                    </div>
                </div>

                <!-- Project 2: Placeholder -->
                <div class="col-lg-6 mb-4">
                    <div class="card project-card h-100">
                        <div class="card-body d-flex align-items-center justify-content-center"
                             style="min-height: 300px; background: #f0f0f0;">
                            <p class="text-muted">Coming Soon</p>
                        </div>
                        <div class="card-body">
                            <h5 class="card-title">Presidential Quotes Analysis</h5>
                            <p class="card-text">
                                NLP analysis of presidential speech patterns and word frequency.
                            </p>
                            <div class="mb-3">
                                <span class="tech-badge">Python</span>
                                <span class="tech-badge">NLP</span>
                                <span class="tech-badge">Plotly</span>
                            </div>
                            <button class="btn btn-secondary" disabled>Coming Soon</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </section>

    <!-- Skills Section -->
    <section id="skills" class="py-5 bg-white">
        <div class="container">
            <h2 class="text-center mb-5">Technical Skills</h2>
            <div class="row text-center">
                <div class="col-md-3 mb-4">
                    <h4>Languages</h4>
                    <p>Python, SQL, DAX</p>
                </div>
                <div class="col-md-3 mb-4">
                    <h4>Tools</h4>
                    <p>Power BI, Tableau, Excel</p>
                </div>
                <div class="col-md-3 mb-4">
                    <h4>Cloud</h4>
                    <p>Azure, GCP, AWS</p>
                </div>
                <div class="col-md-3 mb-4">
                    <h4>Data Engineering</h4>
                    <p>Airflow, ADF, Pandas</p>
                </div>
            </div>
        </div>
    </section>

    <!-- Footer -->
    <footer class="py-4 bg-dark text-white text-center">
        <div class="container">
            <p class="mb-0">Alex Data | <a href="mailto:alex@example.com" class="text-white">alex@example.com</a></p>
            <p class="mt-2">
                <a href="https://linkedin.com/in/alexdata" class="text-white me-3">LinkedIn</a>
                <a href="https://github.com/alexdata" class="text-white">GitHub</a>
            </p>
        </div>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

## Step 3: Create Project Page

**`projects/retail-forecast/index.html`**

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Retail Sales Forecasting | Alex Data</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="assets/style.css">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <div class="container">
            <a class="navbar-brand" href="../../">Alex Data</a>
            <span class="navbar-text">Retail Sales Forecasting</span>
        </div>
    </nav>

    <main class="container py-5">
        <!-- Header -->
        <div class="row mb-5">
            <div class="col-lg-8">
                <h1>Retail Sales Forecasting System</h1>
                <p class="lead">
                    End-to-end data pipeline that forecasts U.S. retail sales
                    and explains prediction errors.
                </p>
                <div class="d-flex gap-2 mt-3">
                    <a href="https://github.com/alexdata/retail-sales-forecast"
                       class="btn btn-dark" target="_blank">
                        View on GitHub
                    </a>
                    <a href="report.pdf" class="btn btn-outline-primary" download>
                        Download Report (PDF)
                    </a>
                </div>
            </div>
            <div class="col-lg-4">
                <div class="card">
                    <div class="card-body">
                        <h5>Project Highlights</h5>
                        <ul class="list-unstyled">
                            <li>MAPE: 3.2%</li>
                            <li>Coverage: 87%</li>
                            <li>Forecast horizon: 6 months</li>
                        </ul>
                    </div>
                </div>
            </div>
        </div>

        <!-- Dashboard Preview -->
        <section class="mb-5">
            <h2>Interactive Dashboard</h2>
            <p>Explore the forecast with confidence intervals.</p>

            <!-- Embedded Plotly Chart -->
            <div class="ratio ratio-16x9 mb-4">
                <iframe src="assets/forecast-chart.html" allowfullscreen></iframe>
            </div>
        </section>

        <!-- Power BI Screenshots -->
        <section class="mb-5">
            <h2>Power BI Dashboard</h2>
            <div class="row">
                <div class="col-md-6 mb-3">
                    <img src="assets/dashboard-1.png" class="img-fluid rounded shadow"
                         alt="Executive Summary">
                    <p class="text-muted mt-2">Executive Summary View</p>
                </div>
                <div class="col-md-6 mb-3">
                    <img src="assets/dashboard-2.png" class="img-fluid rounded shadow"
                         alt="Forecast Detail">
                    <p class="text-muted mt-2">Forecast with Confidence Bands</p>
                </div>
            </div>
        </section>

        <!-- Technical Details -->
        <section class="mb-5">
            <h2>Technical Approach</h2>
            <div class="row">
                <div class="col-md-4">
                    <div class="card h-100">
                        <div class="card-body">
                            <h5>Data Pipeline</h5>
                            <p>Automated ETL using Apache Airflow. Ingests Census Bureau API data monthly.</p>
                            <small class="text-muted">Python, Airflow, Parquet</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card h-100">
                        <div class="card-body">
                            <h5>Forecasting</h5>
                            <p>Facebook Prophet with custom holiday effects and COVID regressors.</p>
                            <small class="text-muted">Prophet, Scikit-learn</small>
                        </div>
                    </div>
                </div>
                <div class="col-md-4">
                    <div class="card h-100">
                        <div class="card-body">
                            <h5>Key Insight</h5>
                            <p>Model explains WHY predictions fail - holidays, COVID, trend shifts.</p>
                            <small class="text-muted">Anomaly Detection</small>
                        </div>
                    </div>
                </div>
            </div>
        </section>

        <!-- Architecture Diagram -->
        <section class="mb-5">
            <h2>System Architecture</h2>
            <pre class="bg-light p-4 rounded"><code>
Census API → Airflow → Transform → Prophet → Power BI
    ↓           ↓          ↓          ↓          ↓
  JSON      Raw Data   Features   Forecast   Dashboard
            </code></pre>
        </section>
    </main>

    <footer class="py-4 bg-dark text-white text-center">
        <p><a href="../../" class="text-white">Back to Portfolio</a></p>
    </footer>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

## Step 4: Export Plotly Charts

Create a script to export interactive charts:

**`scripts/export_charts.py`**

```python
"""
Export Plotly charts for GitHub Pages
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path


def create_forecast_chart():
    """Create main forecast chart with confidence bands."""
    # Load data
    df = pd.read_parquet("data/processed/retail_sales_clean.parquet")
    forecast = pd.read_csv("data/predictions/forecast_latest.csv")
    forecast['ds'] = pd.to_datetime(forecast['ds'])

    fig = go.Figure()

    # 95% Confidence Band
    fig.add_trace(go.Scatter(
        x=pd.concat([forecast['ds'], forecast['ds'][::-1]]),
        y=pd.concat([forecast['yhat_upper_95'], forecast['yhat_lower_95'][::-1]]),
        fill='toself',
        fillcolor='rgba(25,118,210,0.1)',
        line=dict(color='rgba(255,255,255,0)'),
        name='95% Confidence',
        hoverinfo='skip'
    ))

    # 80% Confidence Band
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
        line=dict(color='#1976D2', width=2),
        hovertemplate='%{x|%b %Y}<br>Forecast: $%{y:,.0f}M<extra></extra>'
    ))

    # Actual values
    fig.add_trace(go.Scatter(
        x=df['ds'],
        y=df['y'],
        mode='markers',
        name='Actual',
        marker=dict(color='#212121', size=6),
        hovertemplate='%{x|%b %Y}<br>Actual: $%{y:,.0f}M<extra></extra>'
    ))

    # Layout
    fig.update_layout(
        title=dict(
            text='Retail Sales Forecast - Food & Beverage Stores',
            font=dict(size=20)
        ),
        xaxis_title='Date',
        yaxis_title='Sales (Millions USD)',
        template='plotly_white',
        hovermode='x unified',
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(l=60, r=30, t=80, b=60)
    )

    return fig


def create_seasonality_chart():
    """Create monthly seasonality pattern chart."""
    df = pd.read_parquet("data/processed/retail_sales_clean.parquet")

    # Average by month
    monthly_avg = df.groupby(df['ds'].dt.month)['y'].mean().reset_index()
    monthly_avg.columns = ['month', 'avg_sales']

    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    monthly_avg['month_name'] = monthly_avg['month'].apply(lambda x: month_names[x-1])

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=monthly_avg['month_name'],
        y=monthly_avg['avg_sales'],
        marker_color='#1976D2',
        hovertemplate='%{x}<br>Avg: $%{y:,.0f}M<extra></extra>'
    ))

    fig.update_layout(
        title='Monthly Seasonality Pattern',
        xaxis_title='Month',
        yaxis_title='Average Sales (Millions USD)',
        template='plotly_white'
    )

    return fig


def export_all():
    """Export all charts to HTML."""
    output_dir = Path("projects/retail-forecast/assets")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Forecast chart
    forecast_fig = create_forecast_chart()
    forecast_fig.write_html(
        output_dir / "forecast-chart.html",
        include_plotlyjs='cdn',
        full_html=True,
        config={'displayModeBar': True, 'responsive': True}
    )
    print(f"Exported: {output_dir / 'forecast-chart.html'}")

    # Seasonality chart
    seasonality_fig = create_seasonality_chart()
    seasonality_fig.write_html(
        output_dir / "seasonality-chart.html",
        include_plotlyjs='cdn',
        full_html=True
    )
    print(f"Exported: {output_dir / 'seasonality-chart.html'}")


if __name__ == "__main__":
    export_all()
```

Run:
```bash
python scripts/export_charts.py
```

## Step 5: Export Power BI Screenshots

1. Open Power BI Desktop
2. Navigate to each dashboard page
3. File > Export > Export to PDF
4. Open PDF and screenshot each page, or use:
   - macOS: Cmd + Shift + 4
   - Windows: Snipping Tool

Save as:
- `projects/retail-forecast/assets/dashboard-1.png`
- `projects/retail-forecast/assets/dashboard-2.png`
- etc.

## Step 6: Deploy to GitHub Pages

### Initialize Git Repository

```bash
cd alexdata.github.io

# Initialize git
git init

# Add all files
git add .

# Commit
git commit -m "Initial portfolio deployment"

# Add remote
git remote add origin https://github.com/alexdata/alexdata.github.io.git

# Push
git push -u origin main
```

### Enable GitHub Pages

1. Go to repository Settings
2. Pages (left sidebar)
3. Source: Deploy from a branch
4. Branch: main, / (root)
5. Save

Site will be live at: `https://alexdata.github.io`

### Verify Deployment

```bash
# Check deployment status
gh api repos/alexdata/alexdata.github.io/pages

# Or visit
open https://alexdata.github.io
```

## Step 7: Add Project Repository

For the detailed project code:

```bash
# In project directory
cd project_01_retail_forecast

# Initialize git
git init

# Create .gitignore
cat > .gitignore << 'EOF'
# Environment
.env
venv/
__pycache__/

# Data (keep schemas, not actual data)
data/raw/*
data/processed/*
data/predictions/*
!data/raw/.gitkeep
!data/processed/.gitkeep
!data/predictions/.gitkeep

# Models
models/*.pkl

# IDE
.idea/
.vscode/

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Airflow
airflow.db
airflow.cfg
EOF

# Create .gitkeep files
touch data/raw/.gitkeep
touch data/processed/.gitkeep
touch data/predictions/.gitkeep

# Add files
git add .
git commit -m "Initial project setup with documentation"

# Create GitHub repo and push
gh repo create retail-sales-forecast --public --source=. --push
```

## Step 8: Add GitHub Actions (Optional)

Automate pipeline runs with GitHub Actions:

**`.github/workflows/update_forecast.yml`**

```yaml
name: Update Forecast

on:
  schedule:
    - cron: '0 6 1 * *'  # 1st of month at 6 AM
  workflow_dispatch:  # Manual trigger

jobs:
  forecast:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run pipeline
        env:
          CENSUS_API_KEY: ${{ secrets.CENSUS_API_KEY }}
        run: |
          python src/main.py

      - name: Export charts
        run: |
          python scripts/export_charts.py

      - name: Commit and push
        run: |
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add data/predictions/*.csv projects/retail-forecast/assets/*.html
          git commit -m "Update forecast $(date +%Y-%m-%d)" || exit 0
          git push
```

Add secret:
1. Repository Settings > Secrets and variables > Actions
2. New repository secret: `CENSUS_API_KEY`

## Checklist

Before launching:

- [ ] All HTML pages render correctly
- [ ] Plotly charts are interactive
- [ ] Power BI screenshots are clear
- [ ] Links work (GitHub, LinkedIn, email)
- [ ] Mobile responsive
- [ ] PDF report downloadable
- [ ] README.md is complete
- [ ] .gitignore excludes sensitive files
- [ ] No API keys in code

## Final Result

Your portfolio will be live at:

- **Main site:** https://alexdata.github.io
- **Retail project:** https://alexdata.github.io/projects/retail-forecast/
- **Code repository:** https://github.com/alexdata/retail-sales-forecast

Congratulations! Your data analytics portfolio is now live.
