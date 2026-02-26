# Funding Rate Mean Reversion (Perps)

## Synopsis
Derived from source research and normalized into testable rules.

## Source Context
- Source: DAX test run
- Extract: No extract available

## Hypothesis
Price/funding imbalances around trend exhaustion can be captured with regime-aware entries and strict risk caps.

## Market / Instrument
- Crypto perpetual futures (Bybit initially)
- Start on liquid majors, then expand

## Entry Rules (Draft)
1. Trend filter: price above/below EMA(200)
2. Trigger: RSI pullback + momentum re-acceleration
3. Confirm: funding/mark-index divergence not opposing position

## Exit Rules (Draft)
- Hard stop: 0.5% adverse move
- Take profit ladder: 1R / 2R / trail remainder
- Time stop: close stale position after fixed bars

## Risk Rules
- Max risk per trade: 0.5–1.0% equity
- Daily max loss: 2–3R then disable strategy for session
- Max concurrent positions: 1–2 per symbol cluster

## Data Requirements
- OHLCV candles (1m/5m/15m)
- Funding + mark/index spread
- Volume and volatility features

## Backtest Plan
- In-sample + out-of-sample split
- Walk-forward windows
- Include fees/slippage
- Track Sharpe, max DD, win rate, expectancy

## Confluence Gate (GPT)
- Final decision output: ALLOW / BLOCK / REDUCE_SIZE with rationale
