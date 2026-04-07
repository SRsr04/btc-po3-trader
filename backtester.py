"""
backtester.py — Historical Pattern Backtester

Replays the same 5-step PO3 state machine on historical M1 data.
Lets you validate the strategy without waiting for live candles.

Usage:
    python backtester.py

You will be prompted for the same inputs as the live version:
    Direction, Range High, Range Low, Target Level
"""

import pandas as pd
from data_feed import get_exchange, fetch_candles
from phase_a import get_setup_from_user, validate_setup, print_setup_summary
from phase_d import calculate_entry
from config import SYMBOL, TIMEFRAME_LTF, SL_BUFFER_PCT


# ─────────────────────────────────────────────
# HISTORICAL DATA
# ─────────────────────────────────────────────

BACKTEST_CANDLES = 1440   # last 1440 M1 candles = ~24 hours


def fetch_historical_ltf(limit: int = BACKTEST_CANDLES) -> pd.DataFrame:
    exchange = get_exchange()
    return fetch_candles(exchange, SYMBOL, TIMEFRAME_LTF, limit)


# ─────────────────────────────────────────────
# FRACTAL HELPERS (same logic as phase_m.py)
# ─────────────────────────────────────────────

def check_fractal_low(df, i: int):
    """Fractal Low at index i: low[i] < low[i-1] and low[i] < low[i+1]"""
    if i < 1 or i >= len(df) - 1:
        return None
    if df.iloc[i]["low"] < df.iloc[i-1]["low"] and df.iloc[i]["low"] < df.iloc[i+1]["low"]:
        return df.iloc[i]["low"]
    return None


def check_fractal_high(df, i: int):
    """Fractal High at index i: high[i] > high[i-1] and high[i] > high[i+1]"""
    if i < 1 or i >= len(df) - 1:
        return None
    if df.iloc[i]["high"] > df.iloc[i-1]["high"] and df.iloc[i]["high"] > df.iloc[i+1]["high"]:
        return df.iloc[i]["high"]
    return None


# ─────────────────────────────────────────────
# PATTERN SCANNER
# ─────────────────────────────────────────────

def scan_pattern(df: pd.DataFrame, setup: dict) -> list[dict]:
    """
    Iterates through historical candles candle-by-candle,
    running the same state machine as phase_m.py.
    Returns a list of all confirmed pattern dicts found.
    """
    direction  = setup["direction"]
    range_low  = setup["range_low"]
    range_high = setup["range_high"]

    results = []

    state = {
        "phase"        : "WAITING",
        "f1"           : None, "f2"          : None,
        "f1_time"      : None, "f2_time"     : None,
        "resweep_low"  : None, "resweep_high": None,
        "resweep_time" : None,
    }

    # We need i+1 confirmed for fractals, so range ends at len-1
    for i in range(1, len(df) - 1):
        candle = df.iloc[i]
        close  = candle["close"]
        low    = candle["low"]
        high   = candle["high"]
        ts     = df.index[i]

        if direction == "LONG":

            if state["phase"] == "WAITING":
                if close < range_low:
                    state["phase"] = "SWEPT"

            elif state["phase"] == "SWEPT":
                f1 = check_fractal_low(df, i)
                if f1 is not None and f1 < range_low:
                    state.update({"phase": "F1", "f1": f1, "f1_time": ts})

            elif state["phase"] == "F1":
                f2 = check_fractal_high(df, i)
                if f2 is not None:
                    state.update({"phase": "F2", "f2": f2, "f2_time": ts})

            elif state["phase"] == "F2":
                if low < state["f1"] and close > state["f1"]:
                    state.update({"phase": "RESWEPT", "resweep_low": low, "resweep_time": ts})

            elif state["phase"] == "RESWEPT":
                if close > state["f2"]:
                    state["phase"] = "CONFIRMED"
                    trade = calculate_entry(setup, state, close)
                    results.append({**state, **trade, "confirm_time": ts, "direction": direction})
                    # Reset for next pattern
                    state = {
                        "phase"        : "WAITING",
                        "f1"           : None, "f2"          : None,
                        "f1_time"      : None, "f2_time"     : None,
                        "resweep_low"  : None, "resweep_high": None,
                        "resweep_time" : None,
                    }

        elif direction == "SHORT":

            if state["phase"] == "WAITING":
                if close > range_high:
                    state["phase"] = "SWEPT"

            elif state["phase"] == "SWEPT":
                f1 = check_fractal_high(df, i)
                if f1 is not None and f1 > range_high:
                    state.update({"phase": "F1", "f1": f1, "f1_time": ts})

            elif state["phase"] == "F1":
                f2 = check_fractal_low(df, i)
                if f2 is not None:
                    state.update({"phase": "F2", "f2": f2, "f2_time": ts})

            elif state["phase"] == "F2":
                if high > state["f1"] and close < state["f1"]:
                    state.update({"phase": "RESWEPT", "resweep_high": high, "resweep_time": ts})

            elif state["phase"] == "RESWEPT":
                if close < state["f2"]:
                    state["phase"] = "CONFIRMED"
                    trade = calculate_entry(setup, state, close)
                    results.append({**state, **trade, "confirm_time": ts, "direction": direction})
                    state = {
                        "phase"        : "WAITING",
                        "f1"           : None, "f2"          : None,
                        "f1_time"      : None, "f2_time"     : None,
                        "resweep_low"  : None, "resweep_high": None,
                        "resweep_time" : None,
                    }

    return results


# ─────────────────────────────────────────────
# RESULTS PRINTER
# ─────────────────────────────────────────────

def print_results(results: list[dict], setup: dict):
    total = len(results)
    print(f"\n{'='*50}")
    print(f"  BACKTEST RESULTS — {setup['direction']}")
    print(f"  Symbol    : {SYMBOL}")
    print(f"  Range     : {setup['range_low']} — {setup['range_high']}")
    print(f"  Target    : {setup['target_level']}")
    print(f"  Candles   : {BACKTEST_CANDLES} M1 (~{BACKTEST_CANDLES//60}h)")
    print(f"{'='*50}")
    print(f"  Patterns found : {total}")

    if total == 0:
        print("  No patterns detected in this window.\n")
        return

    for idx, r in enumerate(results, 1):
        print(f"\n  ── Pattern #{idx} ──────────────────────────")
        print(f"  Confirmed at : {r['confirm_time']}")
        print(f"  Entry        : {r['entry_price']:.2f}")
        print(f"  SL           : {r['sl']:.2f}  (risk: ${r['risk']:.2f})")
        print(f"  TP           : {r['tp']:.2f}  (reward: ${r['reward']:.2f})")
        print(f"  R/R          : 1 : {r['rr']}")
        print(f"  F1           : {r['f1']:.2f}  [{r['f1_time']}]")
        print(f"  F2           : {r['f2']:.2f}  [{r['f2_time']}]")

    print(f"\n{'='*50}\n")


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

def main():
    setup = get_setup_from_user()

    if not validate_setup(setup):
        print("\n  Setup invalid. Please restart.")
        return

    print_setup_summary(setup)

    print(f"  Fetching {BACKTEST_CANDLES} historical M1 candles...")
    df = fetch_historical_ltf()
    print(f"  Loaded {len(df)} candles from {df.index[0]} to {df.index[-1]}\n")

    print("  Scanning for PO3 patterns...")
    results = scan_pattern(df, setup)
    print_results(results, setup)


if __name__ == "__main__":
    main()
