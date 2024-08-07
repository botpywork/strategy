import requests
import pandas as pd

# Function to fetch data from Alpha Vantage
def fetch_data(symbol, interval, api_key):
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&apikey={api_key}'
    response = requests.get(url)
    
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception(f"Error fetching data: {response.status_code}")

# Function to convert data to list of dictionaries
def convert_to_list(data, interval):
    time_series_key = f'Time Series ({interval})'
    if time_series_key in data:
        time_series = data[time_series_key]
        data_list = [
            {'timestamp': timestamp,
             'open': float(values['1. open']),
             'high': float(values['2. high']),
             'low': float(values['3. low']),
             'close': float(values['4. close']),
             'volume': int(values['5. volume'])}
            for timestamp, values in time_series.items()
        ]
        return data_list
    else:
        raise KeyError(f"Key '{time_series_key}' not found in data")

# Define your parameters
symbol = 'GBPUSD'
interval = '60min'
api_key = 'TI33YPAL6K683YME'

# Fetch and process the data
try:
    data = fetch_data(symbol, interval, api_key)
    data_list = convert_to_list(data, interval)
    
    # Convert the list to a DataFrame
    df = pd.DataFrame(data_list)
    
    # Save DataFrame to CSV
    df.to_csv('EURUSD_60min_data.csv', index=False)
    
    print("Data saved to 'EURUSD_60min_data.csv'")
    
except Exception as e:
    print(f"An error occurred: {e}")
