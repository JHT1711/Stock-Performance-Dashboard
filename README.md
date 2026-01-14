# Stock Performance Dashboard

An interactive stock performance dashboard built with Python and Streamlit. Analyze price trends, moving averages, and portfolio returns.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![yfinance](https://img.shields.io/badge/yfinance-API-orange)

## Features

- **Multi-Stock Analysis** — Compare multiple stocks side by side
- **Price Charts** — Interactive candlestick charts with moving averages
- **Moving Averages** — Customizable short and long MA periods
- **Volume Analysis** — Trading volume visualization
- **Portfolio Comparison** — Compare cumulative returns across stocks
- **CSV Export** — Download stock data for further analysis

## Tech Stack

| Tool | Purpose |
|------|---------|
| Python | Core programming language |
| Streamlit | Web dashboard framework |
| yfinance | Yahoo Finance API for stock data |
| Plotly | Interactive charts |
| pandas | Data manipulation |

## Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/JHT1711/Stock-Performance-Dashboard.git
cd Stock-Performance-Dashboard
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the dashboard
```bash
streamlit run app.py
```

### 5. Open in browser
Go to http://localhost:8501

## How to Use

1. Enter stock tickers (comma separated) in the sidebar
2. Adjust the date range with the slider
3. Customize moving average periods
4. Click **Fetch Data**
5. Explore individual stock tabs or Portfolio Comparison
6. Download CSV data for any stock

## Screenshots

### Dashboard Overview
- Interactive price charts with moving averages
- Key metrics: Current Price, Total Return, Volatility
- Volume analysis
- Cumulative returns visualization

### Portfolio Comparison
- Side-by-side return comparison
- Performance summary table

## Skills Demonstrated

- **Python** — Data processing and API integration
- **Streamlit** — Interactive web dashboard development
- **yfinance** — Financial data API
- **Plotly** — Data visualization
- **pandas** — Data manipulation and analysis

## Author

**Jaikhush Thakkar**  
Double Major in Applied Statistics & Economics | Penn State University  
[GitHub](https://github.com/JHT1711) • [LinkedIn](https://www.linkedin.com/in/jaikhush-thakkar/)

---

*Disclaimer: This dashboard is for educational purposes only and does not constitute financial advice.*
