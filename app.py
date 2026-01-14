import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config
st.set_page_config(page_title="Stock Dashboard", page_icon="📈", layout="wide")

# Title
st.title("📈 Stock Performance Dashboard")
st.markdown("Analyze stock price trends, moving averages, and portfolio returns")

# Sidebar
st.sidebar.header("Settings")
tickers_input = st.sidebar.text_input("Stock Tickers (comma separated)", "AAPL, MSFT, GOOGL")
tickers = [t.strip().upper() for t in tickers_input.split(",")]

days = st.sidebar.slider("Days of History", 30, 365, 180)

st.sidebar.subheader("Moving Averages")
ma_short = st.sidebar.slider("Short MA (days)", 5, 50, 20)
ma_long = st.sidebar.slider("Long MA (days)", 20, 200, 50)

# Fetch data
if st.sidebar.button("Fetch Data", type="primary"):
    with st.spinner("Fetching data..."):
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        stock_data = {}
        for ticker in tickers:
            df = yf.download(ticker, start=start_date, end=end_date, progress=False)
            if not df.empty:
                df[f'MA_{ma_short}'] = df['Close'].rolling(window=ma_short).mean()
                df[f'MA_{ma_long}'] = df['Close'].rolling(window=ma_long).mean()
                df['Daily_Return'] = df['Close'].pct_change()
                df['Cumulative_Return'] = (1 + df['Daily_Return']).cumprod() - 1
                stock_data[ticker] = df
        
        if stock_data:
            # Create tabs
            tab_names = list(stock_data.keys()) + ["Portfolio Comparison"]
            tabs = st.tabs(tab_names)
            
            # Individual stock tabs
            for i, ticker in enumerate(stock_data.keys()):
                with tabs[i]:
                    df = stock_data[ticker]
                    
                    # Metrics
                    st.subheader(f"{ticker} Key Metrics")
                    col1, col2, col3, col4 = st.columns(4)
                    
                    current_price = float(df['Close'].iloc[-1])
                    start_price = float(df['Close'].iloc[0])
                    total_return = float(df['Cumulative_Return'].iloc[-1]) * 100
                    volatility = float(df['Daily_Return'].std()) * (252 ** 0.5) * 100
                    
                    col1.metric("Current Price", f"${current_price:.2f}")
                    col2.metric("Start Price", f"${start_price:.2f}")
                    col3.metric("Total Return", f"{total_return:.2f}%")
                    col4.metric("Volatility", f"{volatility:.2f}%")
                    
                    # Price chart
                    st.subheader("Price Chart with Moving Averages")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name="Close", line=dict(color='blue')))
                    fig.add_trace(go.Scatter(x=df.index, y=df[f'MA_{ma_short}'], name=f"MA {ma_short}", line=dict(color='orange')))
                    fig.add_trace(go.Scatter(x=df.index, y=df[f'MA_{ma_long}'], name=f"MA {ma_long}", line=dict(color='red')))
                    fig.update_layout(height=500, xaxis_title="Date", yaxis_title="Price ($)")
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Volume
                    st.subheader("Trading Volume")
                    fig_vol = go.Figure()
                    fig_vol.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color='lightblue'))
                    fig_vol.update_layout(height=300, xaxis_title="Date", yaxis_title="Volume")
                    st.plotly_chart(fig_vol, use_container_width=True)
                    
                    # Returns
                    st.subheader("Cumulative Returns")
                    fig_ret = go.Figure()
                    fig_ret.add_trace(go.Scatter(x=df.index, y=df['Cumulative_Return']*100, fill='tozeroy', line=dict(color='green')))
                    fig_ret.update_layout(height=400, xaxis_title="Date", yaxis_title="Return (%)")
                    st.plotly_chart(fig_ret, use_container_width=True)
                    
                    # Download
                    csv = df.to_csv()
                    st.download_button(f"Download {ticker} CSV", csv, f"{ticker}_data.csv", "text/csv")
            
            # Portfolio Comparison tab
            with tabs[-1]:
                st.subheader("Portfolio Comparison")
                
                # Returns comparison chart
                fig_compare = go.Figure()
                for ticker, df in stock_data.items():
                    fig_compare.add_trace(go.Scatter(x=df.index, y=df['Cumulative_Return']*100, name=ticker))
                fig_compare.update_layout(title="Cumulative Returns Comparison", height=500, xaxis_title="Date", yaxis_title="Return (%)")
                st.plotly_chart(fig_compare, use_container_width=True)
                
                # Summary table
                st.subheader("Performance Summary")
                summary = []
                for ticker, df in stock_data.items():
                    summary.append({
                        'Ticker': ticker,
                        'Current Price': f"${float(df['Close'].iloc[-1]):.2f}",
                        'Total Return': f"{float(df['Cumulative_Return'].iloc[-1])*100:.2f}%",
                        'Volatility': f"{float(df['Daily_Return'].std())*(252**0.5)*100:.2f}%"
                    })
                st.dataframe(pd.DataFrame(summary), use_container_width=True, hide_index=True)
        else:
            st.error("No data found for the selected tickers")
else:
    st.info("👈 Enter stock tickers and click 'Fetch Data' to begin")
