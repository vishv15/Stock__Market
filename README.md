# Stock Analysis Dashboard

A Django-based web application for stock analysis, technical indicators, candlestick pattern recognition, and stock forecasting using machine learning models.

## 🔧 Tech Stack

[![Python](https://img.shields.io/badge/Python-3.8+-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org)&nbsp;
[![Django](https://img.shields.io/badge/Django-3.x-green?style=for-the-badge&logo=django&logoColor=white)](https://www.djangoproject.com/)&nbsp;
[![yfinance](https://img.shields.io/badge/yfinance-lightgrey?style=for-the-badge)](https://pypi.org/project/yfinance/)&nbsp;
[![scikit-learn](https://img.shields.io/badge/Scikit--Learn-orange?style=for-the-badge&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)&nbsp;
[![matplotlib](https://img.shields.io/badge/Matplotlib-orange?style=for-the-badge&logo=matplotlib&logoColor=white)](https://matplotlib.org/)&nbsp;
[![plotly](https://img.shields.io/badge/Plotly-blue?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/)


---

![Dashboard Screenshot](static/charts/dashboard_example.png)

## 📊 Features

- **User Authentication:**
  - Secure registration, login, and logout functionality using Django's built-in authentication system.
  
- **Interactive Stock Price Charts:**
  - View stock price trends in **candlestick** and **line chart** formats, powered by `plotly` and `mplfinance`.
  
- **Technical Indicators:**
  - Gain insights into stock performance using **RSI**, **MACD**, **Bollinger Bands**, and other popular technical indicators.
  
- **Candlestick Pattern Detection:**
  - Recognize key candlestick patterns like **Bullish Engulfing**, **Bearish Engulfing**, **Hammer**, **Doji**, etc.
  
- **Stock Screener:**
  - Filter and analyze stocks based on key financial metrics like **P/E ratio**, **market cap**, **price-to-book ratio**, and more.
  
- **Stock Price Forecasting:**
  - Predict future stock prices using advanced **machine learning models** like **Random Forest**, **SVM**, **Decision Trees**, and **Linear Regression**.
  
- **Download & Store Historical Data:**
  - Efficient CSV storage for fast access to historical stock data, allowing for quick analysis and data retrieval.
  
- **Advanced Analytics:**
  - Use machine learning models for deep market analysis and investment decision-making.

## Demo
![Register](static/charts/Login.png)


## Requirements

- Python 3.8+
- Django
- yfinance
- pandas
- numpy
- scikit-learn
- matplotlib
- plotly
- mplfinance
- TA-Lib
- xgboost (optional)

## Setup Instructions

1. **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd <your-repo-directory>
    ```
2. **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3. **Run migrations:**
    ```bash
    python manage.py migrate
    ```
4. **Start the development server:**
    ```bash
    python manage.py runserver
    ```
5. **Access the app:**
    Open your browser and go to [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

## Usage

- Register and log in to access the dashboard.
- Enter stock symbols to view charts and technical indicators.
- Use the screener to analyze financial metrics.
- Forecast stock prices using the forecasting tool.

## Folder Structure

- `stocks/stock_data/views.py` - Main Django views and logic
- `stocks/stock_data/templates/stock_data/` - HTML templates
- `stocks/stock_data/static/charts/` - Example images and chart outputs
- `stocks/stock_data/models.py` - Django models

## Example Screenshots

### Dashboard
![Dashboard](static/charts/dashboard_example.png)

### Candlestick Chart
![Candlestick Chart](static/charts/Chart.png)

### Stock Screener
![Stock Screener](static/charts/Screener.png)

### Pattern Recognition
![Pattern Recognition](static/charts/Pattern.png)

### Forcast
![Forcast](static/charts/Forcast.png)

## License

MIT License

---

*This project is for educational purposes. Please do your own research before making investment decisions.*