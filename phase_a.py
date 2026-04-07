"""
phase_a.py — Phase A: Accumulation (Manual Range Input)

The trader manually defines:
    - Direction    : LONG or SHORT
    - Range High   : upper boundary of the accumulation range
    - Range Low    : lower boundary of the accumulation range
    - Target Level : significant H4/W1 level (used as Take Profit)

This module validates the input and returns a structured setup dict
that all other phases will use.
"""


# ─────────────────────────────────────────────
# INPUT & VALIDATION
# ─────────────────────────────────────────────

def get_setup_from_user() -> dict:
    """
    Asks the trader to input setup parameters via terminal.
    Validates all inputs before returning.

    Returns a setup dict:
        {
            "direction"    : "LONG" or "SHORT",
            "range_high"   : float,
            "range_low"    : float,
            "target_level" : float,
        }
    """
    print("\n" + "="*45)
    print("       PO3 STRATEGY — SETUP INPUT")
    print("="*45)

    # --- Direction ---
    while True:
        direction = input("\nDirection (LONG / SHORT): ").strip().upper()
        if direction in ("LONG", "SHORT"):
            break
        print("  Invalid. Please type LONG or SHORT.")

    # --- Range High ---
    while True:
        try:
            range_high = float(input("Range High: ").strip())
            if range_high > 0:
                break
            print("  Must be a positive number.")
        except ValueError:
            print("  Invalid number. Example: 70179.53")

    # --- Range Low ---
    while True:
        try:
            range_low = float(input("Range Low: ").strip())
            if range_low > 0 and range_low < range_high:
                break
            elif range_low >= range_high:
                print("  Range Low must be less than Range High.")
            else:
                print("  Must be a positive number.")
        except ValueError:
            print("  Invalid number. Example: 69081.51")

    # --- Target Level ---
    while True:
        try:
            target_level = float(input("Target Level (H4/W1 significant level): ").strip())
            if target_level > 0:
                break
            print("  Must be a positive number.")
        except ValueError:
            print("  Invalid number. Example: 71500.00")

    setup = {
        "direction"    : direction,
        "range_high"   : range_high,
        "range_low"    : range_low,
        "target_level" : target_level,
        "range_size"   : round(range_high - range_low, 2),
    }

    return setup


def validate_setup(setup: dict) -> bool:
    """
    Validates that the setup makes logical sense for the chosen direction.

    LONG  : target level must be ABOVE range high (we aim for levels above)
    SHORT : target level must be BELOW range low  (we aim for levels below)
    """
    if setup["direction"] == "LONG":
        if setup["target_level"] <= setup["range_high"]:
            print("\n  Warning: For LONG, target level should be above Range High.")
            print(f"     Range High   : {setup['range_high']}")
            print(f"     Target Level : {setup['target_level']}")
            return False

    elif setup["direction"] == "SHORT":
        if setup["target_level"] >= setup["range_low"]:
            print("\n  Warning: For SHORT, target level should be below Range Low.")
            print(f"     Range Low    : {setup['range_low']}")
            print(f"     Target Level : {setup['target_level']}")
            return False

    return True


def print_setup_summary(setup: dict):
    """Prints a clean summary of the confirmed setup."""
    print("\n" + "="*45)
    print("         SETUP CONFIRMED")
    print("="*45)
    print(f"  Direction    : {setup['direction']}")
    print(f"  Range High   : {setup['range_high']}")
    print(f"  Range Low    : {setup['range_low']}")
    print(f"  Range Size   : ${setup['range_size']}")
    print(f"  Target Level : {setup['target_level']}")
    print("="*45)
    print("\n  Watching for manipulation sweep...\n")


# ─────────────────────────────────────────────
# QUICK TEST
# ─────────────────────────────────────────────

if __name__ == "__main__":
    setup = get_setup_from_user()

    if validate_setup(setup):
        print_setup_summary(setup)
    else:
        print("\n  Setup invalid. Please restart and re-enter values.")