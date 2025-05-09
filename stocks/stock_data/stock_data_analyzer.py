import streamlit as st
import requests
import pandas as pd

# Set page title
st.title("Stock Data Analyzer")

# Fetch stock data from Django API
api_url = "http://127.0.0.1:8000/stock_data/api/stocks/"
response = requests.get(api_url)

if response.status_code == 200:
    stock_data = response.json()
    df = pd.DataFrame(stock_data)

    # Display the stock data in a table
    st.write("Stock Data", df)

    # You can add more analysis or charts here
    st.line_chart(df['price'])
else:
    st.error("Failed to fetch stock data from the API.")
