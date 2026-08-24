---
name: ruflo-neural-trader
description: >-
  Use when building AI-driven trading systems, setting up neural trading agents,
  running backtests on trading strategies, coordinating multi-agent financial
  analysis, or working with the neural-trader npm package via ruflo. Triggers
  on: "ruflo neural trader", "AI trading agents", "neural trading", "backtesting
  trading strategy", "multi-agent trading", "ruflo finance", "trading swarm",
  "financial AI agents", "112 trading tools", "ruflo trader", "automated
  trading AI".
---

# Ruflo Neural Trader — AI Trading System

`ruflo-neural-trader` wraps the `neural-trader` npm package in a 4-agent
ruflo swarm, adding backtesting, 112+ specialized tools, and multi-agent
consensus to financial decision-making.

> **Risk disclaimer:** This plugin is a research and educational tool. Nothing
> here constitutes financial advice. Always validate strategies with a
> compliance review before any live trading.

## Install

```bash
# Requires ruflo-core (and optionally ruflo-swarm for the full 4-agent mode)
claude plugin install ruflo-neural-trader@ruflo
```

This also installs `neural-trader` as an npm dependency in
`~/.ruflo/plugins/ruflo-neural-trader/`.

## The 4-Agent Architecture

```
                    ┌──────────────────┐
                    │  Orchestrator    │
                    │  (Queen Agent)   │
                    │  ─ strategy gate │
                    │  ─ risk limits   │
                    └────────┬─────────┘
          ┌──────────────────┼──────────────────┐
          │                  │                  │
   ┌──────▼──────┐  ┌────────▼──────┐  ┌───────▼────────┐
   │   Market    │  │  Backtesting  │  │  Risk/Portfolio │
   │  Analyst    │  │    Agent      │  │    Manager      │
   │ ─ signals   │  │ ─ historical  │  │ ─ position size │
   │ ─ patterns  │  │   simulation  │  │ ─ drawdown ctrl │
   │ ─ sentiment │  │ ─ metrics     │  │ ─ correlation   │
   └─────────────┘  └───────────────┘  └────────────────┘
```

| Agent | Role |
|---|---|
| **Orchestrator** | Gates trade decisions, enforces risk rules, synthesizes agent outputs |
| **Market Analyst** | Reads price feeds, detects patterns, scores signals |
| **Backtesting Agent** | Simulates strategies on historical data, computes metrics |
| **Risk/Portfolio Manager** | Sizes positions, enforces drawdown limits, tracks correlation |

## The 112+ Tools

Tools are namespaced under `mcp__plugin_ruflo-neural-trader_ruflo__*`.
Categories:

| Category | Tool examples |
|---|---|
| **Market data** | `get_ohlcv`, `get_orderbook`, `get_ticker`, `stream_trades` |
| **Technical indicators** | `sma`, `ema`, `rsi`, `macd`, `bollinger_bands`, `atr`, `vwap` (40+ indicators) |
| **Pattern recognition** | `detect_head_shoulders`, `detect_double_top`, `detect_wedge` |
| **Strategy builders** | `create_strategy`, `add_entry_rule`, `add_exit_rule`, `set_position_size` |
| **Backtesting** | `run_backtest`, `get_metrics`, `plot_equity_curve`, `monte_carlo_sim` |
| **Risk management** | `calc_var`, `calc_cvar`, `check_drawdown`, `calc_kelly_fraction` |
| **Portfolio** | `get_positions`, `rebalance`, `calc_correlation_matrix` |
| **Execution** | `submit_order` (paper trading only by default), `cancel_order`, `get_fills` |

## Quick Start

### 1. Define a strategy (natural language → agent converts to rules)

In a Claude Code session:

```
Create a mean-reversion strategy for BTC/USD:
- Entry: RSI(14) < 30 AND price > 200-day SMA
- Exit: RSI(14) > 60 OR stop-loss 3%
- Position size: 2% of portfolio per trade
- Backtest on 2023-01-01 to 2025-12-31
```

The Orchestrator decomposes this into tasks for each agent and returns a
backtest report.

### 2. Run backtest directly

```
run_backtest({
  "strategy_id": "mean_reversion_btc_v1",
  "symbol": "BTC/USD",
  "timeframe": "1h",
  "start": "2023-01-01",
  "end": "2025-12-31",
  "initial_capital": 100000,
  "commission": 0.001
})
```

### 3. Review metrics

```
get_metrics({ "backtest_id": "bt_abc123" })
```

Returns:

```json
{
  "total_return": 0.847,
  "sharpe_ratio": 1.92,
  "max_drawdown": -0.183,
  "win_rate": 0.61,
  "profit_factor": 2.14,
  "total_trades": 347,
  "avg_trade_duration_hours": 18.4
}
```

## Backtesting Workflow

```
1. Define strategy rules (entry, exit, position sizing)
       │
2. Market Analyst validates signal quality on training window
       │
3. Backtesting Agent runs simulation on test window (walk-forward)
       │
4. Risk/Portfolio Manager checks metrics against risk limits:
       │    - max drawdown < 20%
       │    - Sharpe ratio > 1.0
       │    - Win rate > 40%
       │
5. Orchestrator gates: APPROVE / REJECT / REQUEST_REVISION
       │
6. If approved → paper trading mode (no real orders by default)
```

## Risk Controls

Built-in hard limits enforced by the Risk/Portfolio Manager:

| Control | Default | Config key |
|---|---|---|
| Max position size | 5% of portfolio | `risk.max_position_pct` |
| Max drawdown halt | 15% | `risk.max_drawdown_halt` |
| Daily loss limit | 3% | `risk.daily_loss_limit` |
| Kelly fraction cap | 25% | `risk.kelly_cap` |
| Correlation limit | 0.7 | `risk.max_correlation` |

These can be tightened but **not disabled** without editing the plugin source.

## Configuration

In `~/.ruflo/config.json`:

```json
{
  "neural_trader": {
    "paper_trading": true,
    "data_providers": ["binance", "alpaca", "yfinance"],
    "default_timeframe": "1h",
    "risk": {
      "max_position_pct": 0.05,
      "max_drawdown_halt": 0.15,
      "daily_loss_limit": 0.03,
      "kelly_cap": 0.25,
      "max_correlation": 0.7
    },
    "backtest": {
      "walk_forward_splits": 5,
      "monte_carlo_runs": 1000,
      "commission": 0.001,
      "slippage": 0.0005
    }
  }
}
```

## Multi-Agent Consensus on Trade Decisions

When `ruflo-swarm` is also installed, the 4 agents use a weighted vote before
any trade signal is escalated to the Orchestrator:

```yaml
consensus:
  mode: weighted_vote
  weights:
    market-analyst: 0.35
    backtesting-agent: 0.40    # highest weight: evidence-based
    risk-portfolio-manager: 0.25
  threshold: 0.60              # 60% weighted agreement required
```

A signal that fails to clear 0.60 is logged but not executed.

## Paper Trading vs Live Trading

`ruflo-neural-trader` defaults to **paper trading** (`paper_trading: true`).
In paper mode, `submit_order` simulates fills using historical order book data —
no real money moves.

To enable live trading:

1. Set `paper_trading: false` in config
2. Configure a broker API key in `~/.ruflo/secrets.json` (never in source)
3. The Orchestrator will add an extra confirmation gate requiring explicit
   approval for each trade above a configurable size threshold

> Live trading carries real financial risk. Engage only after thorough
> backtesting, risk review, and compliance sign-off.

## Example: Full Strategy Research Session

```markdown
## Session goal
Research and backtest a momentum strategy for tech stocks.

## Step 1 — Signal discovery (Market Analyst)
"Find the top 3 momentum signals for large-cap tech stocks
 over the last 5 years. Include RSI, MACD, and volume-weighted variants."

## Step 2 — Strategy build (Orchestrator composes rules)
"Build a strategy combining the top 2 signals from step 1.
 Entry on signal confluence. Exit on opposite confluence or 5% trailing stop."

## Step 3 — Backtest (Backtesting Agent)
"Backtest on AAPL, MSFT, NVDA from 2020-01-01 to 2025-12-31,
 walk-forward with 5 splits, 1000 Monte Carlo runs."

## Step 4 — Risk check (Risk/Portfolio Manager)
"Evaluate the strategy against all risk controls. Report any limits breached."

## Step 5 — Decision (Orchestrator)
"Gate the strategy. If approved, activate paper trading mode."
```
