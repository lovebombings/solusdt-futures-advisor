import requests
import time
import os

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_futures_price(symbol="SOLUSDT"):
    url = f"https://fapi.binance.com/fapi/v1/ticker/price?symbol={symbol}"
    data = requests.get(url).json()
    return float(data["price"])

def moving_average(prices, period=20):
    if len(prices) < period:
        return None
    return sum(prices[-period:]) / period

def calculate_rsi(prices, period=14):
    if len(prices) < period + 1:
        return None
    gains, losses = 0, 0
    for i in range(-period, 0):
        change = prices[i] - prices[i-1]
        if change > 0:
            gains += change
        else:
            losses -= change
    avg_gain = gains / period
    avg_loss = losses / period
    if avg_loss == 0:
        return 100
    rs = avg_gain / avg_loss
    return 100 - (100 / (1 + rs))

def calculate_macd(prices, fast=12, slow=26, signal=9):
    def ema(prices, period):
        k = 2 / (period + 1)
        ema_values = []
        for i, price in enumerate(prices):
            if i == 0:
                ema_values.append(price)
            else:
                ema_values.append(price * k + ema_values[-1] * (1 - k))
        return ema_values
    if len(prices) < slow + signal:
        return None, None
    ema_fast = ema(prices, fast)
    ema_slow = ema(prices, slow)
    macd_line = [f - s for f, s in zip(ema_fast[-len(ema_slow):], ema_slow)]
    signal_line = ema(macd_line, signal)
    return macd_line[-1], signal_line[-1]

def get_signal(price, ma20, rsi14, macd, macd_signal):
    if price > ma20 and rsi14 < 30 and macd > macd_signal:
        return "STRONG LONG 📈", GREEN
    elif price < ma20 and rsi14 > 70 and macd < macd_signal:
        return "STRONG SHORT 📉", RED
    else:
        return "HOLD ⚖️", YELLOW

def display(prices, signal, color, symbol):
    latest_price = prices[-1]
    sparkline_chars = "▁▂▃▄▅▆▇█"
    min_price, max_price = min(prices), max(prices)
    sparkline = "".join(
        sparkline_chars[int((p - min_price) / (max_price - min_price) * (len(sparkline_chars)-1))]
        if max_price != min_price else "▁"
        for p in prices
    )
    print(f"{symbol} Perpetual Futures - Real-time Dashboard")
    print(f"Price History: {sparkline}")
    print(f"Current Price: {latest_price:.4f}")
    print(f"Signal: {color}{signal}{RESET}")

def futures_bot(symbol="SOLUSDT", interval=0.5):
    prices = []
    last_signal = None
    print(f"Starting {symbol} perpetual futures bot (updates every {interval} sec)...")
    while True:
        try:
            price = get_futures_price(symbol)
        except:
            print("Error fetching price. Retrying...")
            time.sleep(interval)
            continue

        prices.append(price)
        if len(prices) > 50:
            prices.pop(0)

        ma20 = moving_average(prices, 20)
        rsi14 = calculate_rsi(prices, 14)
        macd, macd_signal = calculate_macd(prices)
        if ma20 is None or rsi14 is None or macd is None:
            time.sleep(interval)
            continue

        signal, color = get_signal(price, ma20, rsi14, macd, macd_signal)

        # Alert if signal changed
        if signal != last_signal:
            print("\a")  # Terminal bell
            last_signal = signal

        clear_terminal()
        display(prices, signal, color, symbol)
        time.sleep(interval)

if __name__ == "__main__":
    futures_bot()
