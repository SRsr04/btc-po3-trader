"""
data_feed.py — Live OHLCV data fetching from Binance
Fetches M15 and M1 candles, filters to Kyiv session window.
"""

import ccxt
import pandas as pd
import pytz
from datetime import datetime
from config import (
    SYMBOL,
    TIMEFRAME_HTF,
    TIMEFRAME_LTF,
    TIMEZONE,
    SESSION_START,
    SESSION_END,
    HTF_CANDLES_LIMIT,
    LTF_CANDLES_LIMIT,
)

# ─────────────────────────────────────────────
# EXCHANGE CONNECTION
# ─────────────────────────────────────────────

def get_exchange():
    """
    Creates and returns a Binance exchange instance.
    No API key needed — we only read public market data.
    """
    exchange = ccxt.binance({
        "enableRateLimit": True,   # respects Binance rate limits automatically
    })
    return exchange


# ─────────────────────────────────────────────
# RAW CANDLE FETCH
# ─────────────────────────────────────────────

def fetch_candles(exchange, symbol, timeframe, limit):
    """
    Fetches raw OHLCV candles from Binance.

    Returns a DataFrame with columns:
        timestamp, open, high, low, close, volume
    Timestamps are converted to Kyiv local time.
    """
    raw = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)

    df = pd.DataFrame(raw, columns=["timestamp", "open", "high", "low", "close", "volume"])

    # Convert millisecond timestamp → UTC datetime → Kyiv local time
    kyiv_tz = pytz.timezone(TIMEZONE)
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
    df["timestamp"] = df["timestamp"].dt.tz_convert(kyiv_tz)

    df.set_index("timestamp", inplace=True)
    return df


# ─────────────────────────────────────────────
# SESSION FILTER
# ─────────────────────────────────────────────

def filter_session(df):
    """
    Keeps only candles that fall within the 08:00–12:00 Kyiv session window.
    Works correctly for both UTC+2 (winter) and UTC+3 (summer) automatically
    because the timestamps are already in Kyiv local time.
    """
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


# ─────────────────────────────────────────────
# PUBLIC INTERFACE — used by all other modules
# ─────────────────────────────────────────────

def get_htf_data(session_only=True):
    """
    Returns M15 candles (Phase A and M timeframe).
    session_only=True  → only candles inside 08:00–12:00 Kyiv window
    session_only=False → all candles (used by backtester)
    """
    exchange = get_exchange()
    df = fetch_candles(exchange, SYMBOL, TIMEFRAME_HTF, HTF_CANDLES_LIMIT)
    if session_only:
        df = filter_session(df)
    return df


def get_ltf_data(session_only=True):
    """
    Returns M1 candles (Phase D timeframe — MSS and entry detection).
    session_only=True  → only candles inside 08:00–12:00 Kyiv window
    session_only=False → all candles (used by backtester)
    """
    exchange = get_exchange()
    df = fetch_candles(exchange, SYMBOL, TIMEFRAME_LTF, LTF_CANDLES_LIMIT)
    if session_only:
        df = filter_session(df)
    return df


# ─────────────────────────────────────────────
# QUICK TEST — run this file directly to verify
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("Fetching M15 candles (session only)...")
    htf = get_htf_data(session_only=True)
    print(f"M15 candles in session: {len(htf)}")
    print(htf.tail(3))

    print("\nFetching M1 candles (session only)...")
    ltf = get_ltf_data(session_only=True)
    print(f"M1 candles in session: {len(ltf)}")
    print(ltf.tail(3))