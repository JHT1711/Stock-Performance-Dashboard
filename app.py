import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Stock Performance Dashboard",
    page_icon="📈",
    layout="wide"
)

# Title
st.title("📈 Stock Performance Dashboard")
st.markdown("Analyze stock price trends, moving averages, and portfolio returns")

# Sidebar - User Inputs
st.sidebar.header("Settings")

# Stock ticker input
default_tickers = "AAPL, MSFT, GOOGL"
tickers_input = st.sidebar.text_input("Enter Stock Tickers (comma separated)", default_tickers)
tickers = [t.strip().upper() for t in tickers_input.split(",")]

# Date range
col1, col2 = st.sidebar.columns(2)
start_date = col1.date_input("Start Date", datetime.now() - timedelta(days=365))
end_date = col2.date_input("End Date", datetime.now())

# Moving average periods
st.sidebar.subheader("Moving Averages")
ma_short = st.sidebar.slider("Short MA (days)", 5, 50, 20)
ma_long = st.sidebar.slider("Long MA (days)", 20, 200, 50)

# Fetch data button
fetch_data = st.sidebar.button("Fetch Data", type="primary")

# Initialize session state
if 'stock_data' not in st.session_state:
    st.session_state.stock_data = None

# Fetch stock data
@st.cache_data
def get_stock_data(tickers, start, end):
    data = {}
    for ticker in tickers:
        try:
            df = yf.download(ticker, start=start, end=end, progress=False)
            if not df.empty:
                data[ticker] = df
        except Exception as e:
            st.error(f"Error fetching {ticker}: {e}")
    return data

# Calculate moving averages
def add_moving_averages(df, short_period, long_period):
    df = df.copy()
    df[f'MA_{short_period}'] = df['Close'].rolling(window=short_period).mean()
    df[f'MA_{long_period}'] = df['Close'].rolling(window=long_period).mean()
    return df

# Calculate returns
def calculate_returns(df):
    df = df.copy()
    df['Daily_Return'] = df['Close'].pct_change()
    df['Cumulative_Return'] = (1 + df['Daily_Return']).cumprod() - 1
    return df

# Main logic
if fetch_data or st.session_state.stock_data is not None:
    if fetch_data:
        with st.spinner("Fetching stock data..."):
            st.session_state.stock_data = get_stock_data(tickers, start_date, end_date)
    
    stock_data = st.session_state.stock_data
    
    if stock_data:
        # Process each stock
        processed_data = {}
        for ticker, df in stock_data.items():
            df = add_moving_averages(df, ma_short, ma_long)
            df = calculate_returns(df)
            processed_data[ticker] = df
        
        # Create tabs for each stock
        tabs = st.tabs(tickers + ["Portfolio Comparison"])
        
        for i, ticker in enumerate(tickers):
            if ticker in processed_data:
                with tabs[i]:
                    df = processed_data[ticker]
                    
                    # Key metrics
                    col1, col2, col3, col4 = st.columns(4)
                    
                    current_price = df['Close'].iloc[-1]
                    start_price = df['Close'].iloc[0]
                    total_return = ((current_price - start_price) / start_price) * 100
                    volatility = df['Daily_Return'].std() * (252 ** 0.5) * 100
                    
                    # Handle MultiIndex columns from yfinance
                    if isinstance(current_price, pd.Series):
                        current_price = current_price.values[0]
                    if isinstance(start_price, pd.Series):
                        start_price = start_price.values[0]
                    if isinstance(total_return, pd.Series):
                        total_return = total_return.values[0]
                    if isinstance(volatility, pd.Series):
                        volatility = volatility.values[0]
                    
                    col1.metric("Current Price", f"${current_price:.2f}")
                    col2.metric("Start Price", f"${start_price:.2f}")
                    col3.metric("Total Return", f"{total_return:.2f}%")
                    col4.metric("Volatility (Annual)", f"{volatility:.2f}%")
                    
                    # Price chart with moving averages
                    st.subheader(f"{ticker} Price Chart with Moving Averages")
                    
                    fig = go.Figure()
                    
                    # Get close prices (handle MultiIndex)
                    close_prices = df['Close']
                    if isinstance(close_prices, pd.DataFrame):
                        close_prices = close_prices.iloc[:, 0]
                    
                    ma_short_values = df[f'MA_{ma_short}']
                    if isinstance(ma_short_values, pd.DataFrame):
                        ma_short_values = ma_short_values.iloc[:, 0]
                    
                    ma_long_values = df[f'MA_{ma_long}']
                    if isinstance(ma_long_values, pd.DataFrame):
                        ma_long_values = ma_long_values.iloc[:, 0]
                    
                    fig.add_trace(go.Scatter(x=df.index, y=close_prices, name="Close Price", line=dict(color='blue')))
                    fig.add_trace(go.Scatter(x=df.index, y=ma_short_values, name=f"MA {ma_short}", line=dict(color='orange')))
                    fig.add_trace(go.Scatter(x=df.index, y=ma_long_values, name=f"MA {ma_long}", line=dict(color='red')))
                    
                    fig.update_layout(height=500, xaxis_title="Date", yaxis_title="Price ($)")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Volume chart
                    st.subheader("Trading Volume")
                    volume = df['Volume']
                    if isinstance(volume, pd.DataFrame):
                        volume = volume.iloc[:, 0]
                    
                    fig_vol = go.Figure()
                    fig_vol.add_trace(go.Bar(x=df.index, y=volume, name="Volume", marker_color='lightblue'))
                    fig_vol.update_layout(height=300, xaxis_title="Date", yaxis_title="Volume")
                    st.plotly_chart(fig_vol, use_container_width=True)
                    
                    # Cumulative returns chart
                    st.subheader("Cumulative Returns")
                    cum_returns = df['Cumulative_Return']
                    if isinstance(cum_returns, pd.DataFrame):
                        cum_returns = cum_returns.iloc[:, 0]
                    
                    fig_ret = go.Figure()
                    fig_ret.add_trace(go.Scatter(x=df.index, y=cum_returns * 100, name="Cumulative Return", fill='tozeroy', line=dict(color='green')))
                    fig_ret.update_layout(height=400, xaxis_title="Date", yaxis_title="Return (%)")
                    st.plotly_chart(fig_ret, use_container_width=True)
        
        # Portfolio Comparison tab
        with tabs[-1]:
            st.subheader("Portfolio Comparison")
            
            # Cumulative returns comparison
            fig_compare = go.Figure()
            
            for ticker in tickers:
                if ticker in processed_data:
                    df = processed_data[ticker]
                    cum_returns = df['Cumulative_Return']
                    if isinstance(cum_returns, pd.DataFrame):
                        cum_returns = cum_returns.iloc[:, 0]
                    fig_compare.add_trace(go.Scatter(x=df.index, y=cum_returns * 100, name=ticker))
            
            fig_compare.update_layout(
                title="Cumulative Returns Comparison",
                height=500,
                xaxis_title="Date",
                yaxis_title="Return (%)"
            )
            st.plotly_chart(fig_compare, use_container_width=True)
            
            # Summary table
            st.subheader("Performance Summary")
            summary_data = []
            
            for ticker in tickers:
                if ticker in processed_data:
                    df = processed_data[ticker]
                    
                    current_price = df['Close'].iloc[-1]
                    total_return = df['Cumulative_Return'].iloc[-1] * 100
                    volatility = df['Daily_Return'].std() * (252 ** 0.5) * 100
                    
                    # Handle MultiIndex
                    if isinstance(current_price, pd.Series):
                        current_price = current_price.values[0]
                    if isinstance(total_return, pd.Series):
                        total_return = total_return.values[0]
                    if isinstance(volatility, pd.Series):
                        volatility = volatility.values[0]
                    
                    summary_data.append({
                        'Ticker': ticker,
                        'Current Price': f"${current_price:.2f}",
                        'Total Return': f"{total_return:.2f}%",
                        'Volatility': f"{volatility:.2f}%"
                    })
            
            summary_df = pd.DataFrame(summary_data)
            st.dataframe(summary_df, use_container_width=True, hide_index=True)
            
            # Export to CSV
            st.subheader("Export Data")
            for ticker in tickers:
                if ticker in processed_data:
                    csv = processed_data[ticker].to_csv()
                    st.download_button(
                        label=f"Download {ticker} Data (CSV)",
                        data=csv,
                        file_name=f"{ticker}_stock_data.csv",
                        mime="text/csv"
                    )
    else:
        st.warning("No data found for the selected tickers.")
else:
    st.info("👈 Enter stock tickers and click 'Fetch Data' to begin")