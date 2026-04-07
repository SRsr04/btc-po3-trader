"""
signals.py — Single Entry Point

Runs the full PO3 strategy pipeline in sequence:
    1. phase_a  →  trader inputs Direction, Range High/Low, Target Level
    2. phase_m  →  algorithm watches M1 candles until pattern confirms
    3. phase_d  →  prints full trade setup: entry, SL, TP, R/R

Usage:
    python signals.py
"""

from phase_a import get_setup_from_user, validate_setup, print_setup_summary
from phase_m import watch_for_sweep
from phase_d import run_phase_d
from data_feed import get_ltf_data


def main():
    # ── Phase A: Setup Input ──────────────────────────────────────────
    setup = get_setup_from_user()

    if not validate_setup(setup):
        print("\n  Setup invalid. Please restart and re-enter values.")
        return

    print_setup_summary(setup)

    # ── Phase M: Pattern Detection ────────────────────────────────────
    state = watch_for_sweep(setup)

    if state is None or state["phase"] != "CONFIRMED":
        print("\n  No confirmed pattern. Exiting.")
        return

    # ── Phase D: Entry Details ────────────────────────────────────────
    # Use the close of the last confirmed candle as entry price
    df           = get_ltf_data(session_only=False)
    entry_price  = df.iloc[-2]["close"]

    run_phase_d(setup, state, entry_price)


if __name__ == "__main__":
    main()
