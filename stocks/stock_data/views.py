from django.shortcuts import render, redirect, reverse
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
import yfinance as yf
import datetime as dt
import pandas as pd
import plotly.graph_objects as go
import os
from django.core.files.storage import FileSystemStorage
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
import mplfinance as mpf
import matplotlib.pyplot as plt
import io
import talib as ta
import base64
from datetime import datetime
import matplotlib.dates as mdates
from django.shortcuts import render
from datetime import datetime, timedelta

from .models import CandlestickPattern 
import requests

from sklearn.linear_model import LinearRegression
from io import BytesIO

@login_required
def dashboard(request):
    return render(request, 'stock_data/stock_dashboard.html')


# --- Configuration ---
DOWNLOAD_DIR = "stock_data"
if not os.path.exists(DOWNLOAD_DIR):
    os.makedirs(DOWNLOAD_DIR)

def format_number(x):
    if isinstance(x, (int, float)):
        return "{:,.0f}".format(x)
    return x

def highlight_max(s):
    if pd.api.types.is_numeric_dtype(s):
        is_max = s == s.max()
        return ['background-color: yellow' if v else '' for v in is_max]
    else:
        return ['' for _ in s]

def download_and_store_data(stock_symbol, start_date, end_date, download_dir):
    """Downloads stock data from yfinance and saves it to a CSV file."""
    file_name = f"{stock_symbol}_{start_date.strftime('%Y-%m-%d')}_{end_date.strftime('%Y-%m-%d')}.csv"
    file_path = os.path.join(download_dir, file_name)

    try:
        hist_price = yf.download(stock_symbol, start=start_date, end=end_date)

        if hist_price is None or hist_price.empty:
            return None  # Indicate failure

        hist_price.reset_index(inplace=True)
        hist_price.to_csv(file_path, index=False)
        return file_path

    except Exception as e:
        print(f"Error processing data download for {stock_symbol}: {e}")
        return None
    


def register_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        if password1 != password2:
            messages.error(request, "Passwords do not match!")
            return render(request, 'stock_data/register.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return render(request, 'stock_data/register.html')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()
        login(request, user)
        return redirect(reverse('chart_page'))  # ✅ Using reverse() to avoid NoReverseMatch

    return render(request, 'stock_data/register.html')

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.GET.get("next") or request.POST.get("next") or "stock_dashboard"
            return redirect(next_url)  # Redirect to dashboard or intended page
        else:
            messages.error(request, "Invalid username or password")  

    return render(request, 'stock_data/login.html')


def logout_view(request):
    logout(request)
    return redirect('login_view')  # Redirect to login page after logout

@login_required # (login_url='/login/')
def chart_page(request):
    stock_symbols = []
    start_date = None
    end_date = None
    chart_type = "Candlestick"  # Default

    if request.method == "POST":  # Data from form submission
        stock_symbols_str = request.POST.get("stock_symbols", "")
        stock_symbols = [s.strip().upper() for s in stock_symbols_str.split(",") if s.strip()]  # Split comma separated
        start_date_str = request.POST.get("start_date", "")
        end_date_str = request.POST.get("end_date", "")
        chart_type = request.POST.get("chart_type", "Candlestick")  # Get selected chart type

        try:
            start_date = dt.datetime.strptime(start_date_str, "%Y-%m-%d").date()  # yyyy-mm-dd string format
            end_date = dt.datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            start_date = dt.date.today() - dt.timedelta(days=90)  # today - 90 days
            end_date = dt.date.today()

        # Download Data (only for chart)
        all_data = {}
        for stock_symbol in stock_symbols:
            file_path = download_and_store_data(stock_symbol, start_date, end_date, DOWNLOAD_DIR)
            if file_path:
                try:
                    all_data[stock_symbol] = pd.read_csv(file_path)
                except Exception as e:
                    print(f"Error reading CSV for {stock_symbol}: {e}")

        chart_htmls = {} # Dictionary to hold chart HTML for each stock
        #what has changed is here!
        if stock_symbols:
            #we only want to work with the first symbol
            stock_symbol = stock_symbols[0]

            for stock_symbol, hist_price in all_data.items():
                # Data Cleaning and Preparation
                try:
                    hist_price['Date'] = pd.to_datetime(hist_price['Date']).dt.date
                    hist_price.set_index('Date', inplace=True)

                    # Chart Generation
                    fig = go.Figure()

                    if chart_type == "Candlestick":
                        fig.add_trace(
                            go.Candlestick(
                                x=hist_price.index,
                                open=hist_price['Open'],
                                high=hist_price['High'],
                                low=hist_price['Low'],
                                close=hist_price['Close'],
                                name='OHLC'
                            )
                        )
                    elif chart_type == "Line Chart":
                        fig.add_trace(
                            go.Scatter(
                                x=hist_price.index,
                                y=hist_price['Close'],
                                mode='lines',
                                name='Closing Price',
                            )
                        )

                    fig.update_layout(
                        title={
                            'text': f'Stock Prices of {stock_symbol}',
                            'x': 0.5,
                            'xanchor': 'center',
                            'font': {'size': 20, 'color': '#E0E0E0'}
                        },
                        plot_bgcolor='rgba(0,0,0,0)',
                        paper_bgcolor='rgba(0,0,0,0)',
                        font_color="#E0E0E0",

                        xaxis=dict(
                            gridcolor='#6B7280',
                            zerolinecolor='#6B7280'
                        ),
                        yaxis=dict(
                            gridcolor='#6B7280',
                            zerolinecolor='#6B7280'
                        )
                    )
                    chart_html = fig.to_html(full_html=False)  # Get chart as HTML fragment
                    chart_htmls[stock_symbol] = chart_html #Store generated chart html
                    print(f"Chart HTML generated for {stock_symbol}")  # Debugging

                except Exception as e:
                    print(f"Error processing data/chart for {stock_symbol}: {e}")

            url = reverse('data_page', kwargs={
                'stock_symbol': stock_symbol,
                'start_date': start_date.strftime('%Y-%m-%d'),  # Format date to string
                'end_date': end_date.strftime('%Y-%m-%d'),      # Format date to string
                'chart_type': chart_type
            })
            context = {}  # dictionary
            context['chart_html'] = chart_html
            context['url'] = url
            print(f"Redirecting to: {url}")  # Debugging
            return render(request, 'stock_data/chart_page.html',context)
        else:
            print("No stock symbol entered")
            context = {}  # dictionary #set context variable here since the redirection is not happening
            context['error_message'] = "Please input a stock symbol"  # error handling
            return render(request, 'stock_data/chart_page.html', context)
    else:  # Initial GET request - default values
        return render(request, 'stock_data/chart_page.html', {})

def data_page(request, stock_symbol, start_date, end_date, chart_type): #get url parameter
    try:
        start_date = dt.datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = dt.datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        # Handle invalid date format if necessary
        return render(request, 'stock_data/error_page.html', {'error_message': 'Invalid date format'})


    file_path = download_and_store_data(stock_symbol, start_date, end_date, DOWNLOAD_DIR)
    if file_path:
        try:
            hist_price = pd.read_csv(file_path)
            # Company Information (moved inside try block to ensure its available)
            stock = yf.Ticker(stock_symbol)
            info = stock.info

            context = {}
            context['stock_symbol'] = stock_symbol #we don't want to use a list anymore, just the one symbol
            context['company_name'] = info.get('longName', 'N/A')
            context['sector'] = info.get('sector', 'N/A')
            context['industry'] = info.get('industry', 'N/A')
            context['website'] = info.get('website', 'N/A')
            context['business_summary'] = info.get('longBusinessSummary', 'N/A')

            context['dividends_html'] = get_financial_data_html(stock.dividends, 'Dividends')
            context['financials_html'] = get_financial_data_html(stock.financials, 'Financials')
            context['balance_sheet_html'] = get_financial_data_html(stock.balance_sheet, 'Balance Sheet')
            context['quarterly_financials_html'] = get_financial_data_html(stock.quarterly_financials, 'Quarterly Financials')
            context['cashflow_html'] = get_financial_data_html(stock.cashflow, 'Cashflow')

            return render(request, 'stock_data/data_page.html', context)
        except Exception as e:
            return render(request, 'stock_data/error_page.html', {'error_message': f"Error processing data: {e}"})
    else:
        return render(request, 'stock_data/error_page.html', {'error_message': 'Failed to download data'})

def get_financial_data_html(df, title):
    if df is not None and not df.empty:
        try:
            if isinstance(df, pd.Series):
                df = df.to_frame()

            styled_df = df.style.apply(highlight_max, axis=1).format(formatter=format_number)
            html_table = styled_df.to_html(classes='table table-striped', table_id=f'{title.lower().replace(" ", "_")}_table')
            return f"<h3>{title}</h3><div class='table-container'>{html_table}</div>"
        except Exception as e:
            print(f"Error displaying {title}: {e}")
            return f"<p>Error displaying {title}: {e}</p>"
    else:
        return f"<p>No {title} data available.</p>"
def data_page(request, stock_symbol, start_date, end_date, chart_type): #get url parameter
    try:
        start_date = dt.datetime.strptime(start_date, "%Y-%m-%d").date()
        end_date = dt.datetime.strptime(end_date, "%Y-%m-%d").date()
    except ValueError:
        # Handle invalid date format if necessary
        return render(request, 'stock_data/error_page.html', {'error_message': 'Invalid date format'})


    file_path = download_and_store_data(stock_symbol, start_date, end_date, DOWNLOAD_DIR)
    if file_path:
        try:
            hist_price = pd.read_csv(file_path)
            # Company Information (moved inside try block to ensure its available)
            stock = yf.Ticker(stock_symbol)
            info = stock.info

            context = {}
            context['stock_symbol'] = stock_symbol #we don't want to use a list anymore, just the one symbol
            context['company_name'] = info.get('longName', 'N/A')
            context['sector'] = info.get('sector', 'N/A')
            context['industry'] = info.get('industry', 'N/A')
            context['website'] = info.get('website', 'N/A')
            context['business_summary'] = info.get('longBusinessSummary', 'N/A')

            context['dividends_html'] = get_financial_data_html(stock.dividends, 'Dividends')
            context['financials_html'] = get_financial_data_html(stock.financials, 'Financials')
            context['balance_sheet_html'] = get_financial_data_html(stock.balance_sheet, 'Balance Sheet')
            context['quarterly_financials_html'] = get_financial_data_html(stock.quarterly_financials, 'Quarterly Financials')
            context['cashflow_html'] = get_financial_data_html(stock.cashflow, 'Cashflow')

            return render(request, 'stock_data/data_page.html', context)
        except Exception as e:
            return render(request, 'stock_data/error_page.html', {'error_message': f"Error processing data: {e}"})
    else:
        return render(request, 'stock_data/error_page.html', {'error_message': 'Failed to download data'})

def get_financial_data_html(df, title):
    if df is not None and not df.empty:
        try:
            if isinstance(df, pd.Series):
                df = df.to_frame()

            styled_df = df.style.apply(highlight_max, axis=1).format(formatter=format_number)
            html_table = styled_df.to_html(classes='table table-striped', table_id=f'{title.lower().replace(" ", "_")}_table')
            return f"<h3>{title}</h3><div class='table-container'>{html_table}</div>"
        except Exception as e:
            print(f"Error displaying {title}: {e}")
            return f"<p>Error displaying {title}: {e}</p>"
    else:
        return f"<p>No {title} data available.</p>" 
    



def stock_screener(request, symbol='AAPL'):
    if request.GET.get('symbol'):
        symbol = request.GET.get('symbol').upper()

    try:
        stock = yf.Ticker(symbol)
        info = stock.info

        context = {
            'symbol': symbol,
            'short_name': info.get('shortName'),
            'long_name': info.get('longName'),
            'sector': info.get('sector'),
            'industry': info.get('industry'),
            'website': info.get('website'),
            'market_cap': info.get('marketCap'),
            'trailing_pe': info.get('trailingPE'),
            'forward_pe': info.get('forwardPE'),
            'eps': info.get('trailingEps'),
            'dividend_yield': info.get('dividendYield'),
            'dividend_rate': info.get('dividendRate'),
            'beta': info.get('beta'),
            'price_to_book': info.get('priceToBook'),
            'book_value': info.get('bookValue'),
            'enterprise_value': info.get('enterpriseValue'),
            'fifty_two_week_high': info.get('fiftyTwoWeekHigh'),
            'fifty_two_week_low': info.get('fiftyTwoWeekLow'),
            'day_high': info.get('dayHigh'),
            'day_low': info.get('dayLow'),
            'profit_margin': info.get('profitMargins'),
            'gross_margin': info.get('grossMargins'),
            'operating_margin': info.get('operatingMargins'),
            'return_on_assets': info.get('returnOnAssets'),
            'return_on_equity': info.get('returnOnEquity'),
            'debt_to_equity': info.get('debtToEquity'),
            'revenue': info.get('totalRevenue'),
            'gross_profit': info.get('grossProfits'),
            'ebitda': info.get('ebitda'),
            'revenue_per_share': info.get('revenuePerShare'),
            'peg_ratio': info.get('pegRatio'),
            'exchange': info.get('exchange'),
            'currency': info.get('currency'),
            'country': info.get('country'),
        }

        return render(request, 'stock_data/stock_screener.html', context)

    except Exception as e:
        return render(request, 'stock_data/stock_screener.html', {
            'error': f"Error fetching data for '{symbol}': {e}",
            'symbol': symbol
        })
    


def check_for_patterns(stock_symbol):
    try:
        # Fetch stock data
        stock_data = yf.download(stock_symbol, period="60d", interval="1d")

        if stock_data.empty:
            return f"No data available for {stock_symbol}"

        patterns_found = []

        for i in range(1, len(stock_data)):
            curr = stock_data.iloc[i]
            prev = stock_data.iloc[i - 1]

            open_curr = curr['Open']
            close_curr = curr['Close']
            open_prev = prev['Open']
            close_prev = prev['Close']
            low_curr = curr['Low']
            high_curr = curr['High']

            # Bullish Engulfing
            if (close_curr > open_curr and close_prev < open_prev and
                open_curr < close_prev and close_curr > open_prev):
                patterns_found.append(f"{curr.name.date()}: Bullish Engulfing")

            # Bearish Engulfing
            if (close_curr < open_curr and close_prev > open_prev and
                open_curr > close_prev and close_curr < open_prev):
                patterns_found.append(f"{curr.name.date()}: Bearish Engulfing")

            # Hammer (simplified)
            real_body = abs(close_curr - open_curr)
            lower_shadow = open_curr - low_curr if open_curr < close_curr else close_curr - low_curr
            if (real_body < (high_curr - low_curr) * 0.3) and (lower_shadow > real_body * 2):
                patterns_found.append(f"{curr.name.date()}: Hammer")

        if patterns_found:
            return f"Patterns for {stock_symbol}:<br>" + "<br>".join(patterns_found)
        else:
            return f"No patterns found for {stock_symbol}"

    except Exception as e:
        return f"Error fetching data for {stock_symbol}: {str(e)}"
# Django view to render the candlestick patterns page
# utils.py or any helper file
def candlestick_patterns(stock_symbol):

    try:
        # Download stock data
        stock_data = yf.download(stock_symbol, period="1mo", interval="1d")
    except Exception as e:
        return {"error": f"Error fetching data for {stock_symbol}: {str(e)}"}

    # If data is empty, return a message
    if stock_data.empty:
        return {"error": f"No data found for {stock_symbol}."}

    # Calculate max and min between Open and Close
    max_oc = stock_data[['Close', 'Open']].max(axis=1)  # Correctly calculating max row-wise
    min_oc = stock_data[['Close', 'Open']].min(axis=1)  # Correctly calculating min row-wise

    # Calculate Shadows and Body
    stock_data['UpperShadow'] = stock_data['High'] - max_oc
    stock_data['LowerShadow'] = min_oc - stock_data['Low']
    stock_data['Body'] = abs(stock_data['Close'] - stock_data['Open'])

    # Detect Candlestick Patterns
    stock_data['BullishEngulfing'] = (
        (stock_data['Close'] > stock_data['Open']) &
        (stock_data['Close'].shift(1) < stock_data['Open'].shift(1)) &
        (stock_data['Open'] < stock_data['Close'].shift(1)) &
        (stock_data['Close'] > stock_data['Open'].shift(1))
    )

    stock_data['BearishEngulfing'] = (
        (stock_data['Close'] < stock_data['Open']) &
        (stock_data['Close'].shift(1) > stock_data['Open'].shift(1)) &
        (stock_data['Open'] > stock_data['Close'].shift(1)) &
        (stock_data['Close'] < stock_data['Open'].shift(1))
    )

    stock_data['Doji'] = stock_data['Body'] < (stock_data['High'] - stock_data['Low']) * 0.1
    stock_data['Hammer'] = (
        (stock_data['UpperShadow'] < stock_data['Body'] * 0.1) &
        (stock_data['LowerShadow'] > stock_data['Body'] * 2)
    )
    stock_data['ShootingStar'] = (
        (stock_data['UpperShadow'] > stock_data['Body'] * 2) &
        (stock_data['LowerShadow'] < stock_data['Body'] * 0.1)
    )

    # Collect detected patterns
    pattern_names = ['BullishEngulfing', 'BearishEngulfing', 'Doji', 'Hammer', 'ShootingStar']
    patterns_result = []

    for pattern in pattern_names:
        pattern_dates = stock_data[stock_data[pattern]].index.strftime('%Y-%m-%d').tolist()
        for date in pattern_dates:
            patterns_result.append({'pattern': pattern, 'date': date})

    return {"patterns": patterns_result}

def candlestick_patterns_view(request):
    symbol = request.GET.get("symbol", "")
    context = {
        "symbol": symbol,
        "error_message": "",
        "patterns": [],
    }

    if symbol:
        result = candlestick_patterns(symbol)
        if "error" in result:
            context["error_message"] = result["error"]
        else:
            context["patterns"] = result["patterns"]

    return render(request, "stock_data/candlestick_patterns.html", context)



def get_stock_news(symbol):
    # You can use a news API to fetch the latest news for the stock symbol
    url = f'https://newsapi.org/v2/everything?q={symbol}&apiKey=YOUR_NEWS_API_KEY'
    response = requests.get(url)
    news_data = response.json()

    return news_data.get('articles', [])

def get_sentiment(news):
    # Simple sentiment analysis: If the article mentions positive words, it's good news; otherwise, bad news.
    positive_keywords = ['increase', 'growth', 'profit', 'positive', 'upward', 'surge']
    negative_keywords = ['decline', 'loss', 'drop', 'negative', 'downward']

    # Check if any of the positive/negative keywords are in the title or description
    sentiment = 'bad'
    for article in news:
        title = article['title']
        description = article['description']

        if any(keyword in title.lower() or keyword in description.lower() for keyword in positive_keywords):
            sentiment = 'good'
        elif any(keyword in title.lower() or keyword in description.lower() for keyword in negative_keywords):
            sentiment = 'bad'
    
    return sentiment
def detect_patterns(df):
    patterns = []
    
    for i in range(1, len(df)):
        row = df.iloc[i]
        prev_row = df.iloc[i - 1]
        
        o, h, l, c = row[['Open', 'High', 'Low', 'Close']]
        po, ph, pl, pc = prev_row[['Open', 'High', 'Low', 'Close']]
        
        # Fix: Access the date directly from DataFrame by position
        date_val = df.iloc[i, df.columns.get_loc('Date')]
        
        # Safely format the date
        if hasattr(date_val, 'strftime'):
            date = date_val.strftime('%Y-%m-%d')
        else:
            date = str(date_val)
        
        body = abs(c - o)
        prev_body = abs(pc - po)
        lower_shadow = min(o, c) - l
        upper_shadow = h - max(o, c)
        
        # Candlestick Pattern Detection
        
        # Doji
        if abs(o - c) < 0.1 * (h - l):
            patterns.append({'name': 'Doji', 'signal': 'Neutral', 'date': date})
        
        # Bullish Engulfing
        if pc > po and c > o and o < pc and c > po:
            patterns.append({'name': 'Bullish Engulfing', 'signal': 'Bullish', 'date': date})
        
        # Bearish Engulfing
        if pc < po and c < o and o > pc and c < po:
            patterns.append({'name': 'Bearish Engulfing', 'signal': 'Bearish', 'date': date})
        
        # Hammer (Bullish)
        if body < lower_shadow and lower_shadow > 2 * body and upper_shadow < body:
            patterns.append({'name': 'Hammer', 'signal': 'Bullish', 'date': date})
        
        # Inverted Hammer (Bullish)
        if body < upper_shadow and upper_shadow > 2 * body and lower_shadow < body:
            patterns.append({'name': 'Inverted Hammer', 'signal': 'Bullish', 'date': date})
        
        # Hanging Man (Bearish)
        if body < lower_shadow and lower_shadow > 2 * body and upper_shadow < body:
            patterns.append({'name': 'Hanging Man', 'signal': 'Bearish', 'date': date})
        
        # Shooting Star (Bearish)
        if body < upper_shadow and upper_shadow > 2 * body and lower_shadow < body:
            patterns.append({'name': 'Shooting Star', 'signal': 'Bearish', 'date': date})
        
        # Bullish Marubozu
        if lower_shadow < 0.05 * body and upper_shadow < 0.05 * body and c > o:
            patterns.append({'name': 'Bullish Marubozu', 'signal': 'Bullish', 'date': date})
        
        # Bearish Marubozu
        if lower_shadow < 0.05 * body and upper_shadow < 0.05 * body and c < o:
            patterns.append({'name': 'Bearish Marubozu', 'signal': 'Bearish', 'date': date})
        
        # Spinning Top
        if body < 0.5 * (h - l) and lower_shadow > 0 and upper_shadow > 0:
            patterns.append({'name': 'Spinning Top', 'signal': 'Neutral', 'date': date})
        
        # Tweezer Bottom (Bullish)
        if c > o and pc < po and abs(l - pl) < 0.1 * l:
            patterns.append({'name': 'Tweezer Bottom', 'signal': 'Bullish', 'date': date})
        
        # Tweezer Top (Bearish)
        if c < o and pc > po and abs(h - ph) < 0.1 * h:
            patterns.append({'name': 'Tweezer Top', 'signal': 'Bearish', 'date': date})
        
        # Bullish Harami
        if abs(pc - po) > abs(c - o) and min(pc, po) < max(c, o) and max(pc, po) > min(c, o) and c > o:
            patterns.append({'name': 'Bullish Harami', 'signal': 'Bullish', 'date': date})
        
        # Bearish Harami
        if abs(pc - po) > abs(c - o) and min(pc, po) < max(c, o) and max(pc, po) > min(c, o) and c < o:
            patterns.append({'name': 'Bearish Harami', 'signal': 'Bearish', 'date': date})
        
        # Bullish Harami Cross (Harami + Doji)
        if abs(pc - po) > abs(c - o) and min(pc, po) < max(c, o) and max(pc, po) > min(c, o) and abs(o - c) < 0.1 * (h - l):
            patterns.append({'name': 'Bullish Harami Cross', 'signal': 'Bullish', 'date': date})
        
        # Bearish Harami Cross (Harami + Doji)
        if abs(pc - po) > abs(c - o) and min(pc, po) < max(c, o) and max(pc, po) > min(c, o) and abs(o - c) < 0.1 * (h - l):
            patterns.append({'name': 'Bearish Harami Cross', 'signal': 'Bearish', 'date': date})
    
    return patterns

def pattern_checker(request):
    context = {}
    if request.method == 'POST':
        symbol = request.POST.get('symbol')
        df = yf.download(symbol, period='30d', interval='1d')
        
        if df.empty:
            context['error'] = "Invalid symbol or no data found."
            return render(request, 'stock_data/pattern_checker.html', context)
        
        df.dropna(inplace=True)
        df.reset_index(inplace=True)  # so we get 'Date' as column
        
        # Ensure Date is datetime type
        df['Date'] = pd.to_datetime(df['Date'])
        
        results = detect_patterns(df.tail(5))  # check last 5 candles
        context['symbol'] = symbol
        context['patterns'] = results
        
        # Add this conditional to show a message when no patterns are found
        if not results:
            context['no_patterns'] = "No patterns detected in the last 5 candles."
    
    return render(request, 'stock_data/pattern_checker.html', context)


def stock_news(request):
    articles = []
    error = None

    if request.method == 'POST':
        symbol = request.POST.get('symbol')
        if symbol:
            # Your MarketAux API Key
            api_key = 'aDMEz9iuiShVYNwVsT848kYqL8iuWawzFTm4eDNS'

            # Generate MarketAux API URL
            url = f"https://api.marketaux.com/v1/news/all?symbols={symbol}&filter_entities=true&language=en&api_token={api_key}"

            # Fetch news
            response = requests.get(url)
            data = response.json()

            if 'data' in data and data['data']:
                articles = data['data']  # ✅ No limit now, show all articles
            else:
                error = "No news found for the given stock symbol."
        else:
            error = "Please enter a stock symbol."

    return render(request, 'stock_data/news_dashboard.html', {
        'articles': articles,
        'error': error
    })

def predict_next_day_stock(symbol):
    try:
        # 1. Fetch data
        data = yf.download(symbol, period="30d", interval="1d")
        if data.empty:
            raise ValueError(f"No data returned for symbol: {symbol}")

        data['Date'] = pd.to_datetime(data.index)
        data = data[['Date', 'Close']]
        data['Day'] = data['Date'].dt.day
        data['Month'] = data['Date'].dt.month
        data['Year'] = data['Date'].dt.year

        X = data[['Year', 'Month', 'Day']]
        y = data['Close']

        # 2. Define models
        models = {
            'Linear Regression': LinearRegression(),
            'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
            'SVR': SVR(kernel='rbf'),
            #'KNN': KNeighborsRegressor(n_neighbors=3),
            'Decision Tree': DecisionTreeRegressor(random_state=42)
        }

        # 3. Next day features
        next_day = datetime.now() + timedelta(days=1)
        next_day_features = [[next_day.year, next_day.month, next_day.day]]

        # 4. Plot setup
        plt.figure(figsize=(12, 6))
        plt.plot(data['Date'], y, label='Actual Price', color='black', linewidth=2)

        predictions_dict = {}
        for name, model in models.items():
            model.fit(X, y)
            predicted_y = model.predict(X)
            predicted_next = model.predict(next_day_features)[0]
            predictions_dict[name] = predicted_next

            # Plot predicted line
            plt.plot(data['Date'], predicted_y, linestyle='--', label=f'{name} Prediction')

            # Plot predicted next day
            plt.scatter(next_day, predicted_next, label=f'{name} Next Day', marker='o', s=80)

        # Final chart tweaks
        plt.title(f'{symbol.upper()} Price Prediction - Multiple Models')
        plt.xlabel('Date')
        plt.ylabel('Close Price (₹)')
        plt.xticks(rotation=45)
        plt.grid(True)
        plt.legend()
        plt.tight_layout()

        # Convert plot to base64
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        chart_img = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close()

        return predictions_dict, chart_img

    except Exception as e:
        raise e

def stock_forecast(request):
    if request.method == 'POST':
        symbol = request.POST.get('stock_symbol')
        if symbol:
            try:
                predictions, chart_img = predict_next_day_stock(symbol)
                return render(request, 'stock_data/stock_forecast.html', {
                    'symbol': symbol,
                    'predictions': predictions,
                    'chart_img': chart_img
                })
            except Exception as e:
                return render(request, 'stock_data/stock_forecast.html', {'error': str(e)})
    return render(request, 'stock_data/stock_forecast.html')

def get_technical_data(symbol, start_date, end_date):
    return yf.download(symbol, start=start_date, end=end_date)

def calculate_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def technical_indicators_view(request, symbol, start_date, end_date, chart_type):
    # 1. Fetch Data
    data = get_technical_data(symbol, start_date, end_date)

    # 2. Calculate Indicators
    data['SMA20'] = data['Close'].rolling(window=20).mean()
    data['EMA20'] = data['Close'].ewm(span=20, adjust=False).mean()
    data['RSI'] = calculate_rsi(data['Close'])
    data['EMA12'] = data['Close'].ewm(span=12, adjust=False).mean()
    data['EMA26'] = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = data['EMA12'] - data['EMA26']
    data['Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()

    # 3. Plotting
    fig, ax = plt.subplots(2, 1, figsize=(12, 8), sharex=True)

    # Top: Close, SMA, EMA
    ax[0].plot(data['Close'], label='Close', color='black')
    ax[0].plot(data['SMA20'], label='SMA 20', color='blue', linestyle='--')
    ax[0].plot(data['EMA20'], label='EMA 20', color='orange', linestyle='--')
    ax[0].set_title(f'{symbol} Close Price + Moving Averages')
    ax[0].legend()
    ax[0].grid(True)

    # Bottom: MACD
    ax[1].plot(data['MACD'], label='MACD', color='purple')
    ax[1].plot(data['Signal'], label='Signal', color='red')
    ax[1].set_title('MACD')
    ax[1].legend()
    ax[1].grid(True)

    plt.tight_layout()

    # 4. Convert to image
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    chart_img = base64.b64encode(buf.read()).decode('utf-8')

    # 5. Convert latest technical values to table
    indicators_df = data[['Close', 'SMA20', 'EMA20', 'RSI', 'MACD', 'Signal']].dropna().tail(30)

    # 6. Render to template
    context = {
        'symbol': symbol,
        'start_date': start_date,
        'end_date': end_date,
        'chart_img': chart_img,
        'data': indicators_df.to_html(classes='table table-bordered', border=0)
    }
    return render(request, 'stock_data/technical_indicators.html', context)