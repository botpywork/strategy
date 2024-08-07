import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import requests

def fetch_currency_data(api_key, from_symbol='GBP', to_symbol='USD'):
    """
    Fetch currency data from Alpha Vantage using the daily time series endpoint.
    
    Parameters:
    api_key : str
        Your Alpha Vantage API key.
    from_symbol : str
        Base currency (e.g., 'GBP').
    to_symbol : str
        Quote currency (e.g., 'USD').
        
    Returns:
    df : pandas.DataFrame
        DataFrame with columns ['Date', 'Close']
    """
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={from_symbol}{to_symbol}&apikey={api_key}'
    response = requests.get(url)
    data = response.json()
    
    if 'Time Series (Daily)' in data:
        df = pd.DataFrame.from_dict(data['Time Series (Daily)'], orient='index')
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        df.index = pd.to_datetime(df.index)
        df = df.sort_index()
        df = df.astype(float)
        df.reset_index(inplace=True)
        df.rename(columns={'index': 'Date'}, inplace=True)
    elif 'Note' in data:
        raise ValueError("Error fetching data from Alpha Vantage: " + data['Note'])
    elif 'Error Message' in data:
        raise ValueError("Error fetching data from Alpha Vantage: " + data['Error Message'])
    else:
        print("Unexpected response structure:", data)
        raise ValueError("Error fetching data from Alpha Vantage: Unknown error")

    return df

def filter_data_by_date(df, start_date, end_date):
    """
    Filter data by a specific date range.
    
    Parameters:
    df : pandas.DataFrame
        DataFrame with columns ['Date', 'Close']
    start_date : str
        Start date in 'YYYY-MM-DD' format.
    end_date : str
        End date in 'YYYY-MM-DD' format.
        
    Returns:
    df : pandas.DataFrame
        Filtered DataFrame
    """
    df['Date'] = pd.to_datetime(df['Date'])
    mask = (df['Date'] >= start_date) & (df['Date'] <= end_date)
    return df.loc[mask]

def detect_trends(df, short_window=50, long_window=200):
    """
    Detect trends in currency prices using moving averages.
    
    Parameters:
    df : pandas.DataFrame
        DataFrame with columns ['Date', 'Close']
    short_window : int
        Window size for the short moving average
    long_window : int
        Window size for the long moving average
    
    Returns:
    df : pandas.DataFrame
        DataFrame with columns ['Date', 'Close', 'Short_MA', 'Long_MA', 'Trend']
    """
    df['Short_MA'] = df['Close'].rolling(window=short_window, min_periods=1).mean()
    df['Long_MA'] = df['Close'].rolling(window=long_window, min_periods=1).mean()
    
    df['Trend'] = np.where(df['Short_MA'] > df['Long_MA'], 'Uptrend', 
                           np.where(df['Short_MA'] < df['Long_MA'], 'Downtrend', 'Sideways'))
    
    return df, short_window, long_window

# Fetch GBP/USD data from Alpha Vantage
api_key = 'TI33YPAL6K683YME'  # Replace with your Alpha Vantage API key
df = fetch_currency_data(api_key)

# Filter data for a specific date range
start_date = '2024-01-01'
end_date = '2024-06-30'
df_filtered = filter_data_by_date(df, start_date, end_date)

# Detect trends
df_filtered, short_window, long_window = detect_trends(df_filtered)

# Plot the data with trends
plt.figure(figsize=(14, 7))
plt.plot(df_filtered['Date'], df_filtered['Close'], label='Close Price')
plt.plot(df_filtered['Date'], df_filtered['Short_MA'], label=f'{short_window}-Day MA')
plt.plot(df_filtered['Date'], df_filtered['Long_MA'], label=f'{long_window}-Day MA')

# Highlight the trends
colors = {'Uptrend': 'green', 'Downtrend': 'red', 'Sideways': 'blue'}
for trend, color in colors.items():
    trend_df = df_filtered[df_filtered['Trend'] == trend]
    plt.scatter(trend_df['Date'], trend_df['Close'], color=color, label=trend, alpha=0.5)

plt.title('GBP/USD Price with Detected Trends')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()
