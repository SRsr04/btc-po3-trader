import ccxt
import pandas as pd
import pytz
from config import (
    SYMBOL, TIMEFRAME_HTF, TIMEFRAME_LTF,
    TIMEZONE, SESSION_START, SESSION_END,
    HTF_CANDLES_LIMIT, LTF_CANDLES_LIMIT,
)

def get_exchange():
    return ccxt.binance({"enableRateLimit": True})

def fetch_candles(exchange, symbol, timeframe, limit):
    raw = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(raw, columns=["timestamp","open","high","low","close","volume"])
    kyiv_tz = pytz.timezone(TIMEZONE)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df["timestamp"] = df["timestamp"].dt.tz_convert(kyiv_tz)
    df.set_index("timestamp", inplace=True)
    return df

def filter_session(df):
    start_h, start_m = map(int, SESSION_START.split(":"))
    end_h,   end_m   = map(int, SESSION_END.split(":"))
    mask = (
        (df.index.hour > start_h) |
        ((df.index.hour == start_h) & (df.index.minute >= start_m))
    ) & (
        (df.index.hour < end_h) |
        ((df.index.hour == end_h) & (df.index.minute <= end_m))
    )
    return df[mask].copy()

def get_htf_data(session_only=True):
    exchange = get_exchange()
    df = fetch_candles(exchange, SYMBOL, TIMEFRAME_HTF, HTF_CANDLES_LIMIT)
    if session_only:
        df = filter_session(df)
    return df

def get_ltf_data(session_only=True):
    exchange = get_exchange()
    df = fetch_candles(exchange, SYMBOL, TIMEFRAME_LTF, LTF_CANDLES_LIMIT)
    if session_only:
        df = filter_session(df)
    return df

if __name__ == "__main__":
    print("Fetching M15 candles...")
    htf = get_htf_data(session_only=False)
    print(f"M15 candles: {len(htf)}")
    print(htf.tail(3))
    print("\nFetching M1 candles...")
    ltf = get_ltf_data(session_only=False)
    print(f"M1 candles: {len(ltf)}")
    print(ltf.tail(3))
