"""
phase_d.py — Phase D: Distribution (Entry Details)

After pattern confirmation in phase_m.py, this module calculates:
    - Stop Loss  : below resweep low (LONG) / above resweep high (SHORT)
    - Take Profit: the target level provided in setup (H4/W1 significant level)
    - Risk/Reward ratio
    - Prints a clean entry card with all trade parameters
"""

from config import SYMBOL


# ─────────────────────────────────────────────
# SL / TP CALCULATION
# ─────────────────────────────────────────────

SL_BUFFER_PCT = 0.001   # 0.1% buffer beyond resweep extreme for SL


def calculate_entry(setup: dict, state: dict, entry_price: float) -> dict:
    """
    Calculates SL, TP, and RR for a confirmed pattern.

    LONG  : SL = resweep_low  * (1 - SL_BUFFER_PCT)
    SHORT : SL = resweep_high * (1 + SL_BUFFER_PCT)
    TP    : target_level from setup in both cases
    """
    direction    = setup["direction"]
    target_level = setup["target_level"]

    if direction == "LONG":
        sl = round(state["resweep_low"] * (1 - SL_BUFFER_PCT), 2)
        tp = target_level
    else:
        sl = round(state["resweep_high"] * (1 + SL_BUFFER_PCT), 2)
        tp = target_level

    risk   = abs(entry_price - sl)
    reward = abs(tp - entry_price)
    rr     = round(reward / risk, 2) if risk > 0 else None

    return {
        "entry_price" : entry_price,
        "sl"          : sl,
        "tp"          : tp,
        "risk"        : round(risk, 2),
        "reward"      : round(reward, 2),
        "rr"          : rr,
    }


# ─────────────────────────────────────────────
# ENTRY CARD PRINTER
# ─────────────────────────────────────────────

def print_entry_card(setup: dict, state: dict, trade: dict):
    direction = setup["direction"]
    side      = "BUY  (LONG)" if direction == "LONG" else "SELL (SHORT)"

    print("\n" + "="*50)
    print("  TRADE SETUP — READY TO EXECUTE")
    print("="*50)
    print(f"  Symbol       : {SYMBOL}")
    print(f"  Direction    : {side}")
    print(f"  Entry Price  : {trade['entry_price']:.2f}")
    print(f"  Stop Loss    : {trade['sl']:.2f}   (risk: ${trade['risk']:.2f})")
    print(f"  Take Profit  : {trade['tp']:.2f}   (reward: ${trade['reward']:.2f})")
    if trade["rr"] is not None:
        print(f"  R/R Ratio    : 1 : {trade['rr']}")
    print("-"*50)
    print(f"  F1           : {state['f1']:.2f}")
    print(f"  F2           : {state['f2']:.2f}")
    if direction == "LONG":
        print(f"  Resweep Low  : {state['resweep_low']:.2f}")
    else:
        print(f"  Resweep High : {state['resweep_high']:.2f}")
    print(f"  BOS confirmed: {state['resweep_time']}")
    print("="*50 + "\n")


# ─────────────────────────────────────────────
# MAIN FUNCTION
# ─────────────────────────────────────────────

def run_phase_d(setup: dict, state: dict, entry_price: float) -> dict:
    """
    Calculates and prints the full entry card.
    Returns the trade dict for use by signals.py.
    """
    trade = calculate_entry(setup, state, entry_price)
    print_entry_card(setup, state, trade)
    return trade


# ─────────────────────────────────────────────
# QUICK TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    # Simulated confirmed state for testing
    mock_setup = {
        "direction"   : "LONG",
        "range_high"  : 70179.53,
        "range_low"   : 69081.51,
        "target_level": 71500.00,
        "range_size"  : 1098.02,
    }
    mock_state = {
        "phase"        : "CONFIRMED",
        "f1"           : 68800.00,
        "f2"           : 69400.00,
        "f1_time"      : "2024-01-15 09:12:00",
        "f2_time"      : "2024-01-15 09:18:00",
        "resweep_low"  : 68750.00,
        "resweep_high" : None,
        "resweep_time" : "2024-01-15 09:24:00",
    }
    mock_entry = 69410.00

    run_phase_d(mock_setup, mock_state, mock_entry)
