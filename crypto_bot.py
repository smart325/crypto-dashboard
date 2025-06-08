import requests
import time
import json
import pandas as pd
import numpy as np

COINS = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "floki": "FLOKI",
    "ordinals": "ORDI",
    "0x": "ZRX",
    "elrond": "EGLD",
    "axie-infinity": "AXS",
    "smooth-love-potion": "SLP",
    "celer-network": "CELR",
    "ether-fi": "ETHF",
    "pingu": "PENGU",
    "manta-network": "MANTA",
    "metis-token": "METIS",
    "scroll": "SCRL",
    "dydx": "DYDX",
    "lukso-token": "LUKSO",
    "optimism": "OP",
    "bonfida": "FIDA",
    "dymension": "DYM",
    "dodo": "DODO",
    "layerzero": "LZ",
    "rocket-pool": "RPL"
}

def fetch_price_history(coin_id, days=30):
    url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart"
    params = {"vs_currency": "usd", "days": days}
    r = requests.get(url, params=params)
    data = r.json()
    prices = data["prices"]
    df = pd.DataFrame(prices, columns=["timestamp", "price"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    df.set_index("timestamp", inplace=True)
    return df

def compute_indicators(df):
    # RSI
    delta = df["price"].diff()
    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)
    avg_gain = gain.rolling(14).mean()
    avg_loss = loss.rolling(14).mean()
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    # MA50, MA200
    ma50 = df["price"].rolling(window=50).mean()
    ma200 = df["price"].rolling(window=200).mean()

    # MACD
    ema12 = df["price"].ewm(span=12, adjust=False).mean()
    ema26 = df["price"].ewm(span=26, adjust=False).mean()
    macd = ema12 - ema26
    signal = macd.ewm(span=9, adjust=False).mean()
    hist = macd - signal

    # Bollinger Bands
    ma20 = df["price"].rolling(window=20).mean()
    std20 = df["price"].rolling(window=20).std()
    upper_band = ma20 + (std20 * 2)
    lower_band = ma20 - (std20 * 2)

    return {
        "rsi": round(rsi.iloc[-1], 2),
        "ma50": round(ma50.iloc[-1], 2),
        "ma200": round(ma200.iloc[-1], 2),
        "macd": round(macd.iloc[-1], 6),
        "macd_signal": round(signal.iloc[-1], 6),
        "macd_hist": round(hist.iloc[-1], 6),
        "bb_upper": round(upper_band.iloc[-1], 2),
        "bb_lower": round(lower_band.iloc[-1], 2),
        "bb_middle": round(ma20.iloc[-1], 2),
        "price_usd": round(df["price"].iloc[-1], 6)
    }

def fetch_eur_usd_rate():
    r = requests.get("https://api.exchangerate.host/latest?base=USD&symbols=EUR")
    data = r.json()
    return data["rates"]["EUR"]

def analyze_signal(indicators):
    rsi = indicators["rsi"]
    price = indicators["price_usd"]
    macd = indicators["macd"]
    macd_signal = indicators["macd_signal"]
    # Signal simple d’exemple : acheter si RSI < 30 ou MACD croise signal à la hausse
    if rsi < 30 or (macd > macd_signal):
        return "BUY"
    elif rsi > 70 or (macd < macd_signal):
        return "SELL"
    else:
        return "HOLD"

def main_loop():
    eur_usd = fetch_eur_usd_rate()
    signals = {}
    while True:
        for coin_id, symbol in COINS.items():
            df = fetch_price_history(coin_id)
            indicators = compute_indicators(df)
            signal = analyze_signal(indicators)
            price_eur = round(indicators["price_usd"] * eur_usd, 6)
            signals[symbol] = {
                "price_usd": indicators["price_usd"],
                "price_eur": price_eur,
                "rsi": indicators["rsi"],
                "ma50": indicators["ma50"],
                "ma200": indicators["ma200"],
                "macd": indicators["macd"],
                "macd_signal": indicators["macd_signal"],
                "macd_hist": indicators["macd_hist"],
                "bb_upper": indicators["bb_upper"],
                "bb_lower": indicators["bb_lower"],
                "bb_middle": indicators["bb_middle"],
                "signal": signal,
                "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            print(f"{symbol}: {signal} at {indicators['price_usd']}$")
        with open("signals.json", "w") as f:
            json.dump(signals, f, indent=4)
        time.sleep(300)  # toutes les 5 minutes

if __name__ == "__main__":
    main_loop()
