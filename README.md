# BTC PO3 Trader

Automated trading signal detector for BTC/USDT on Binance, 
based on the Power of 3 (AMD) strategy.

The trader manually defines the accumulation range and direction. 
The algorithm watches M1 candles in real time and fires a signal 
when the full PO3 pattern is confirmed.

## How It Works

**LONG sequence (after price breaks below Range Low):**
1. Price closes below Range Low → sweep
2. Fractal Low forms below Range Low (F1)
3. Fractal High forms after F1 (F2)
4. Price sweeps below F1 but closes above it (resweep)
5. Price closes above F2 → BOS → ENTRY SIGNAL

SHORT is the mirror logic above Range High.

## Project Structure

| File | Description |
|------|-------------|
| `config.py` | All parameters in one place |
| `data_feed.py` | Fetches M1/M15 OHLCV from Binance via ccxt |
| `phase_a.py` | Terminal input — direction, range, target level |
| `phase_m.py` | Real-time pattern detection state machine |
| `phase_d.py` | Entry signal with SL, TP and R/R calculation |
| `signals.py` | Main entry point — runs all phases in sequence |
| `backtester.py` | Same logic on historical data |
| `notebook.ipynb` | Visualization of patterns and backtest results |

## Quickstart

```bash
git clone https://github.com/SRsr04/btc-po3-trader
cd btc-po3-trader
pip install -r requirements.txt
python signals.py
```

## Example Output

```
Direction   : LONG
Range High  : 70179.53
Range Low   : 69081.51
Target      : 71500.00

[14:23:01] Sweep confirmed — price closed below Range Low
[14:31:44] F1 formed at 68990.12
[14:38:22] F2 formed at 69380.50
[14:44:05] Resweep confirmed
[14:51:33] BOS confirmed — ENTRY SIGNAL

Entry  : 69385.00
SL     : 68921.10  (-0.67%)
TP     : 71500.00  (+3.04%)
R/R    : 1 : 4.5
```

## Stack

Python · ccxt · pandas · Binance API
