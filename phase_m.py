"""
phase_m.py — Phase M: Manipulation (Sweep + Resweep + BOS Detection on M1)

LONG sequence (on M1 after price breaks below Range Low):
    1. WAITING   → price closes below Range Low
    2. F1        → Fractal Low forms (1 candle each side confirms it)
    3. F2        → Fractal High forms after F1 (1 candle each side confirms it)
    4. RESWEPT   → wick goes below F1 BUT candle closes above F1
    5. CONFIRMED → candle body closes above F2 → BOS → ENTRY SIGNAL

SHORT sequence (mirror logic above Range High).

Fractal confirmation:
    A fractal at iloc[-2] is confirmed when iloc[-1] just closed.
    So fractal check always looks at the last 3 candles: [-3], [-2], [-1].
"""

import time
from datetime import datetime, timezone
from data_feed import get_ltf_data


def wait_for_candle_close():
    """Sleeps until the next full minute + 1 second buffer."""
    now = datetime.now(timezone.utc)
    seconds_to_wait = 60 - now.second + 1
    time.sleep(seconds_to_wait)


def check_fractal_low(df):
    """iloc[-2] is Fractal Low if its low < iloc[-3].low AND < iloc[-1].low"""
    if len(df) < 3:
        return None
    left, middle, right = df.iloc[-3], df.iloc[-2], df.iloc[-1]
    if middle["low"] < left["low"] and middle["low"] < right["low"]:
        return middle["low"]
    return None


def check_fractal_high(df):
    """iloc[-2] is Fractal High if its high > iloc[-3].high AND > iloc[-1].high"""
    if len(df) < 3:
        return None
    left, middle, right = df.iloc[-3], df.iloc[-2], df.iloc[-1]
    if middle["high"] > left["high"] and middle["high"] > right["high"]:
        return middle["high"]
    return None


def check_pattern(df, setup: dict, state: dict) -> dict:
    if df is None or len(df) < 3:
        return state

    candle      = df.iloc[-2]
    close       = candle["close"]
    low         = candle["low"]
    high        = candle["high"]
    open_       = candle["open"]
    candle_time = df.index[-2]
    direction   = setup["direction"]
    range_low   = setup["range_low"]
    range_high  = setup["range_high"]

    print(f"  [{candle_time}]  "
          f"O: {open_:.2f}  H: {high:.2f}  L: {low:.2f}  C: {close:.2f}"
          f"  | {state['phase']}")

    if direction == "LONG":

        if state["phase"] == "WAITING":
            if close < range_low:
                state["phase"] = "SWEPT"
                print(f"\n  >>> Price closed below Range Low: {close:.2f} < {range_low}")
                print(f"      Watching for F1 (Fractal Low)...\n")

        elif state["phase"] == "SWEPT":
            f1 = check_fractal_low(df)
            if f1 is not None and f1 < range_low:
                state.update({"phase": "F1", "f1": f1, "f1_time": df.index[-2]})
                print(f"\n  >>> F1 Fractal Low confirmed: {f1:.2f}  [{df.index[-2]}]")
                print(f"      Watching for F2 (Fractal High)...\n")

        elif state["phase"] == "F1":
            f2 = check_fractal_high(df)
            if f2 is not None:
                state.update({"phase": "F2", "f2": f2, "f2_time": df.index[-2]})
                print(f"\n  >>> F2 Fractal High confirmed: {f2:.2f}  [{df.index[-2]}]")
                print(f"      Watching for resweep — wick below F1: {state['f1']:.2f}, close above F1\n")

        elif state["phase"] == "F2":
            if low < state["f1"] and close > state["f1"]:
                state.update({"phase": "RESWEPT", "resweep_low": low, "resweep_time": candle_time})
                print(f"\n  >>> Resweep confirmed  [{candle_time}]")
                print(f"      Wick: {low:.2f} < F1: {state['f1']:.2f} | Close: {close:.2f} > F1 (body above)")
                print(f"      Watching for BOS — close above F2: {state['f2']:.2f}\n")

        elif state["phase"] == "RESWEPT":
            if close > state["f2"]:
                state["phase"] = "CONFIRMED"
                print(f"\n  {'='*50}")
                print(f"  ENTRY SIGNAL — LONG")
                print(f"  {'='*50}")
                print(f"  BOS: close {close:.2f} > F2: {state['f2']:.2f}")
                print(f"  F1 (Fractal Low)  : {state['f1']:.2f}")
                print(f"  F2 (Fractal High) : {state['f2']:.2f}")
                print(f"  Resweep Low       : {state['resweep_low']:.2f}")
                print(f"  Target Level      : {setup['target_level']}")
                print(f"  {'='*50}\n")

    elif direction == "SHORT":

        if state["phase"] == "WAITING":
            if close > range_high:
                state["phase"] = "SWEPT"
                print(f"\n  >>> Price closed above Range High: {close:.2f} > {range_high}")
                print(f"      Watching for F1 (Fractal High)...\n")

        elif state["phase"] == "SWEPT":
            f1 = check_fractal_high(df)
            if f1 is not None and f1 > range_high:
                state.update({"phase": "F1", "f1": f1, "f1_time": df.index[-2]})
                print(f"\n  >>> F1 Fractal High confirmed: {f1:.2f}  [{df.index[-2]}]")
                print(f"      Watching for F2 (Fractal Low)...\n")

        elif state["phase"] == "F1":
            f2 = check_fractal_low(df)
            if f2 is not None:
                state.update({"phase": "F2", "f2": f2, "f2_time": df.index[-2]})
                print(f"\n  >>> F2 Fractal Low confirmed: {f2:.2f}  [{df.index[-2]}]")
                print(f"      Watching for resweep — wick above F1: {state['f1']:.2f}, close below F1\n")

        elif state["phase"] == "F2":
            if high > state["f1"] and close < state["f1"]:
                state.update({"phase": "RESWEPT", "resweep_high": high, "resweep_time": candle_time})
                print(f"\n  >>> Resweep confirmed  [{candle_time}]")
                print(f"      Wick: {high:.2f} > F1: {state['f1']:.2f} | Close: {close:.2f} < F1 (body below)")
                print(f"      Watching for BOS — close below F2: {state['f2']:.2f}\n")

        elif state["phase"] == "RESWEPT":
            if close < state["f2"]:
                state["phase"] = "CONFIRMED"
                print(f"\n  {'='*50}")
                print(f"  ENTRY SIGNAL — SHORT")
                print(f"  {'='*50}")
                print(f"  BOS: close {close:.2f} < F2: {state['f2']:.2f}")
                print(f"  F1 (Fractal High) : {state['f1']:.2f}")
                print(f"  F2 (Fractal Low)  : {state['f2']:.2f}")
                print(f"  Resweep High      : {state['resweep_high']:.2f}")
                print(f"  Target Level      : {setup['target_level']}")
                print(f"  {'='*50}\n")

    return state


def watch_for_sweep(setup: dict) -> dict | None:
    state = {
        "phase": "WAITING",
        "f1": None, "f2": None,
        "f1_time": None, "f2_time": None,
        "resweep_low": None, "resweep_high": None, "resweep_time": None,
    }

    print(f"\n  Syncing to candle close...")
    wait_for_candle_close()
    print(f"  Synced. Checking each closed M1 candle.")
    print(f"  Press Ctrl+C to stop.\n")

    try:
        while state["phase"] != "CONFIRMED":
            df    = get_ltf_data(session_only=False)
            state = check_pattern(df, setup, state)
            if state["phase"] != "CONFIRMED":
                wait_for_candle_close()
    except KeyboardInterrupt:
        print("\n\n  Stopped by user.")
        return None

    return state


if __name__ == "__main__":
    from phase_a import get_setup_from_user, validate_setup, print_setup_summary

    setup = get_setup_from_user()
    if not validate_setup(setup):
        print("\n  Setup invalid. Please restart.")
    else:
        print_setup_summary(setup)
        result = watch_for_sweep(setup)
        if result and result["phase"] == "CONFIRMED":
            print("\n  Pattern confirmed. Ready for entry signal.")