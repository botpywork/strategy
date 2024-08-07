import pandas as pd
import yfinance as yf
import ta

# Define functions to identify candlestick patterns
def is_doji(candle, body_size_threshold=0.1):
    body_size = abs(candle['Close'] - candle['Open'])
    candle_range = candle['High'] - candle['Low']
    if candle_range == 0:  # Prevent division by zero
        return False
    body_percentage = body_size / candle_range
    return body_percentage <= body_size_threshold

def is_hammer(candle, body_size_threshold=0.1, shadow_ratio=2):
    body_size = abs(candle['Close'] - candle['Open'])
    candle_range = candle['High'] - candle['Low']
    lower_shadow = min(candle['Close'], candle['Open']) - candle['Low']
    upper_shadow = candle['High'] - max(candle['Close'], candle['Open'])
    
    if candle_range == 0:  # Prevent division by zero
        return False
    
    body_percentage = body_size / candle_range
    lower_shadow_ratio = lower_shadow / body_size
    upper_shadow_ratio = upper_shadow / body_size
    
    return (body_percentage <= body_size_threshold and
            lower_shadow_ratio >= shadow_ratio and
            upper_shadow_ratio < body_size_threshold)

def is_inverted_hammer(candle, body_size_threshold=0.1, shadow_ratio=2):
    body_size = abs(candle['Close'] - candle['Open'])
    candle_range = candle['High'] - candle['Low']
    lower_shadow = min(candle['Close'], candle['Open']) - candle['Low']
    upper_shadow = candle['High'] - max(candle['Close'], candle['Open'])
    
    if candle_range == 0:  # Prevent division by zero
        return False
    
    body_percentage = body_size / candle_range
    lower_shadow_ratio = lower_shadow / body_size
    upper_shadow_ratio = upper_shadow / body_size
    
    return (body_percentage <= body_size_threshold and
            upper_shadow_ratio >= shadow_ratio and
            lower_shadow_ratio < body_size_threshold)

def is_hanging_man(candle, body_size_threshold=0.1, shadow_ratio=2):
    return is_hammer(candle, body_size_threshold, shadow_ratio) and (candle['Close'] < candle['Open'])

def is_bullish_engulfing(prev_candle, current_candle):
    return (prev_candle['Close'] < prev_candle['Open'] and  # Previous candle was bearish
            current_candle['Close'] > current_candle['Open'] and  # Current candle is bullish
            current_candle['Open'] < prev_candle['Close'] and  # Current candle opens below previous close
            current_candle['Close'] > prev_candle['Open'])  # Current candle closes above previous open

def is_bearish_engulfing(prev_candle, current_candle):
    return (prev_candle['Close'] > prev_candle['Open'] and  # Previous candle was bullish
            current_candle['Close'] < current_candle['Open'] and  # Current candle is bearish
            current_candle['Open'] > prev_candle['Close'] and  # Current candle opens above previous close
            current_candle['Close'] < prev_candle['Open'])  # Current candle closes below previous open

def is_falling_three_methods(data, index):
    if index < 4 or index + 1 >= len(data):
        return False
    first_candle = data.iloc[index - 4]
    second_candle = data.iloc[index - 3]
    third_candle = data.iloc[index - 2]
    fourth_candle = data.iloc[index - 1]
    fifth_candle = data.iloc[index]
    return (first_candle['Close'] < first_candle['Open'] and
            second_candle['Close'] > second_candle['Open'] and
            third_candle['Close'] > third_candle['Open'] and
            fourth_candle['Close'] > fourth_candle['Open'] and
            fifth_candle['Close'] < fourth_candle['Close'] and
            fifth_candle['Close'] < first_candle['Close'])

def is_rising_three_methods(data, index):
    if index < 4 or index + 1 >= len(data):
        return False
    first_candle = data.iloc[index - 4]
    second_candle = data.iloc[index - 3]
    third_candle = data.iloc[index - 2]
    fourth_candle = data.iloc[index - 1]
    fifth_candle = data.iloc[index]
    return (first_candle['Close'] > first_candle['Open'] and
            second_candle['Close'] < second_candle['Open'] and
            third_candle['Close'] < third_candle['Open'] and
            fourth_candle['Close'] < fourth_candle['Open'] and
            fifth_candle['Close'] > fourth_candle['Close'] and
            fifth_candle['Close'] > first_candle['Close'])

def is_evening_star(data, index):
    if index < 2:
        return False
    first_candle = data.iloc[index - 2]
    second_candle = data.iloc[index - 1]
    third_candle = data.iloc[index]
    return (first_candle['Close'] > first_candle['Open'] and  # Bullish first candle
            abs(second_candle['Close'] - second_candle['Open']) < abs(first_candle['Close'] - first_candle['Open']) and  # Small body second candle
            third_candle['Close'] < third_candle['Open'] and  # Bearish third candle
            third_candle['Close'] < (first_candle['Close'] + first_candle['Open']) / 2)  # Close of third candle below midpoint of first candle

def is_morning_star(data, index):
    if index < 2:
        return False
    first_candle = data.iloc[index - 2]
    second_candle = data.iloc[index - 1]
    third_candle = data.iloc[index]
    return (first_candle['Close'] < first_candle['Open'] and  # Bearish first candle
            abs(second_candle['Close'] - second_candle['Open']) < abs(first_candle['Close'] - first_candle['Open']) and  # Small body second candle
            third_candle['Close'] > third_candle['Open'] and  # Bullish third candle
            third_candle['Close'] > (first_candle['Close'] + first_candle['Open']) / 2)  # Close of third candle above midpoint of first candle

def is_three_black_crows(data, index):
    if index < 2:
        return False
    first_candle = data.iloc[index - 2]
    second_candle = data.iloc[index - 1]
    third_candle = data.iloc[index]
    return (first_candle['Close'] < first_candle['Open'] and  # Bearish first candle
            second_candle['Close'] < second_candle['Open'] and  # Bearish second candle
            third_candle['Close'] < third_candle['Open'] and  # Bearish third candle
            first_candle['Close'] > second_candle['Open'] and  # First candle close above second candle open
            second_candle['Close'] > third_candle['Open'])  # Second candle close above third candle open

def is_three_white_soldiers(data, index):
    if index < 2:
        return False
    first_candle = data.iloc[index - 2]
    second_candle = data.iloc[index - 1]
    third_candle = data.iloc[index]
    return (first_candle['Close'] > first_candle['Open'] and  # Bullish first candle
            second_candle['Close'] > second_candle['Open'] and  # Bullish second candle
            third_candle['Close'] > third_candle['Open'] and  # Bullish third candle
            first_candle['Close'] < second_candle['Open'] and  # First candle close below second candle open
            second_candle['Close'] < third_candle['Open'])  # Second candle close below third candle open

def is_bullish_harami(prev_candle, current_candle):
    return (prev_candle['Close'] < prev_candle['Open'] and  # Previous candle was bearish
            current_candle['Close'] > current_candle['Open'] and  # Current candle is bullish
            current_candle['Open'] > prev_candle['Close'] and  # Current candle opens above previous close
            current_candle['Close'] < prev_candle['Open'])  # Current candle closes below previous open

def is_bearish_harami(prev_candle, current_candle):
    return (prev_candle['Close'] > prev_candle['Open'] and  # Previous candle was bullish
            current_candle['Close'] < current_candle['Open'] and  # Current candle is bearish
            current_candle['Open'] < prev_candle['Close'] and  # Current candle opens below previous close
            current_candle['Close'] > prev_candle['Open'])  # Current candle closes above previous open

# Load historical price data at an hourly interval
data = yf.download('EURUSD=X', start='2024-04-01', end='2024-06-01', interval='1h')

# Resample data to 1-hour intervals (if needed, this line is redundant since data is already hourly)
data = data.resample('1h').agg({
    'Open': 'first',
    'High': 'max',
    'Low': 'min',
    'Close': 'last',
    'Volume': 'sum'
})

# Calculate technical indicators
data['MA'] = ta.trend.sma_indicator(data['Close'], window=20)
data['EMA'] = ta.trend.ema_indicator(data['Close'], window=20)
stochastic = ta.momentum.StochasticOscillator(
    high=data['High'], 
    low=data['Low'], 
    close=data['Close'],
    window=14, 
    smooth_window=3
)
data['Stochastic'] = stochastic.stoch()
macd = ta.trend.MACD(data['Close'])
data['MACD'] = macd.macd()
data['MACD_signal'] = macd.macd_signal()
bollinger = ta.volatility.BollingerBands(data['Close'], window=20, window_dev=2)
data['BB_bbm'] = bollinger.bollinger_mavg()
data['BB_bbh'] = bollinger.bollinger_hband()
data['BB_bbl'] = bollinger.bollinger_lband()
data['RSI'] = ta.momentum.RSIIndicator(data['Close'], window=14).rsi()

# Drop rows with NaN values for indicators
data = data.dropna(subset=['MA', 'EMA', 'RSI', 'Stochastic', 'MACD', 'MACD_signal'])

# Function to detect candlestick patterns and create signals
def detect_patterns_and_generate_signals(data):
    signals = []
    for i in range(1, len(data)):
        current_candle = data.iloc[i]
        prev_candle = data.iloc[i - 1]
        
        signal = ''
        if is_doji(current_candle):
            signal = 'Doji'
        elif is_hammer(current_candle):
            signal = 'Hammer'
        elif is_inverted_hammer(current_candle):
            signal = 'Inverted Hammer'
        elif is_hanging_man(current_candle):
            signal = 'Hanging Man'
        elif is_bullish_engulfing(prev_candle, current_candle):
            signal = 'Bullish Engulfing'
        elif is_bearish_engulfing(prev_candle, current_candle):
            signal = 'Bearish Engulfing'
        elif is_falling_three_methods(data, i):
            signal = 'Falling Three Methods'
        elif is_rising_three_methods(data, i):
            signal = 'Rising Three Methods'
        elif is_evening_star(data, i):
            signal = 'Evening Star'
        elif is_morning_star(data, i):
            signal = 'Morning Star'
        elif is_three_black_crows(data, i):
            signal = 'Three Black Crows'
        elif is_three_white_soldiers(data, i):
            signal = 'Three White Soldiers'
        elif is_bullish_harami(prev_candle, current_candle):
            signal = 'Bullish Harami'
        elif is_bearish_harami(prev_candle, current_candle):
            signal = 'Bearish Harami'
        
        # Combine candlestick pattern signal with technical indicators
        if current_candle['Close'] > current_candle['EMA'] and current_candle['RSI'] < 30:
            signal = 'Buy'
        elif current_candle['Close'] < current_candle['EMA'] and current_candle['RSI'] > 70:
            signal = 'Sell'
        
        signals.append(signal)
    
    data['Signal'] = [''] + signals  # Add an empty string for the first row since it has no previous row
    return data

# Apply the pattern detection and signal generation
data = detect_patterns_and_generate_signals(data)

# Print data with signals
print(data.head())

# Save the DataFrame to a CSV file
file_path = 'data_with_signals.csv'
data.to_csv(file_path)
print(f"Data saved to {file_path}")

# Example of executing trades based on signals
def execute_trade(signal, amount):
    if signal == 'Buy':
        print(f"Placing a buy order for {amount} units.")
        # Replace with actual API call
        # api.place_order('BUY', amount)
    elif signal == 'Sell':
        print(f"Placing a sell order for {amount} units.")
        # Replace with actual API call
        # api.place_order('SELL', amount)

# Execute trades based on signals
for index, row in data.iterrows():
    if row['Signal'] in ['Buy', 'Sell']:
        execute_trade(row['Signal'], 1)  # Adjust amount as needed
