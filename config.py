<<<<<<< HEAD
"""
config.py — Central configuration for the PO3 Trading Strategy
All parameters live here. Change values only in this file.
"""
 
# ─────────────────────────────────────────────
# ASSET
# ─────────────────────────────────────────────
SYMBOL         = "BTC/USDT"        # Binance pair
TIMEFRAME_HTF  = "15m"             # Phase A & M: accumulation and sweep detection
TIMEFRAME_LTF  = "1m"             # Phase D: MSS and entry trigger
 
# ─────────────────────────────────────────────
# SESSION WINDOW (Kyiv Time)
# Handles UTC+2 (winter) and UTC+3 (summer) automatically
# ─────────────────────────────────────────────
TIMEZONE          = "Europe/Kyiv"
SESSION_START     = "08:00"        # Kyiv local time
SESSION_END       = "12:00"        # Kyiv local time
 
# ─────────────────────────────────────────────
# PHASE A — ACCUMULATION (Range Detection)
# ─────────────────────────────────────────────
ACCUMULATION_MIN_CANDLES = 6       # Min M15 candles inside range = 1.5 hours
ACCUMULATION_MAX_CANDLES = 8       # Max M15 candles to look back for range
 
# ─────────────────────────────────────────────
# PHASE M — MANIPULATION (Sweep Detection)
# ─────────────────────────────────────────────
FRACTAL_WINDOW        = 1          # Williams fractal: N candles on each side
CLEAN_REJECTION_RATIO = 0.60       # Wick must be >= 60% of total candle range
 
# ─────────────────────────────────────────────
# PHASE D — DISTRIBUTION (Entry Logic)
# ─────────────────────────────────────────────
FVG_MIN_SIZE_PCT = 0.001           # FVG must be >= 0.1% of price to filter noise
ENTRY_VARIANT    = "BOTH"          # "A" = 0.5 retracement | "B" = FVG | "BOTH"
 
# ─────────────────────────────────────────────
# DATA FEED
# ─────────────────────────────────────────────
HTF_CANDLES_LIMIT = 100            # How many M15 candles to fetch per cycle
LTF_CANDLES_LIMIT = 60             # How many M1 candles to fetch per cycle
LIVE_POLL_SECONDS = 60             # How often to re-fetch data in live mode (seconds)
 
=======
SYMBOL         = "BTC/USDT"
TIMEFRAME_HTF  = "15m"
TIMEFRAME_LTF  = "1m"

TIMEZONE          = "Europe/Kyiv"
SESSION_START     = "08:00"
SESSION_END       = "12:00"

ACCUMULATION_MIN_CANDLES = 6
ACCUMULATION_MAX_CANDLES = 8

FRACTAL_WINDOW        = 2
CLEAN_REJECTION_RATIO = 0.60

FVG_MIN_SIZE_PCT = 0.001
ENTRY_VARIANT    = "BOTH"

HTF_CANDLES_LIMIT = 100
LTF_CANDLES_LIMIT = 60
LIVE_POLL_SECONDS = 60
>>>>>>> 2c7f187 (feat: module 2 - data feed)
