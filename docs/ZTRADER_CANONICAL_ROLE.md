# zDash Canonical Trading Role

zDash is the canonical operator dashboard and observability UI for the consolidated trading stack.

Consume:
- zTrader intelligence from `cvsz/zworkforce`
- orders, positions, paper PnL and deterministic risk from `cvsz/zksato`
- on-chain evidence from external standalone `cvsz/zwallet`
- model/provider telemetry from `cvsz/zaiman`

Target views:
- discovery and narratives
- token intelligence
- whale/on-chain evidence
- risk and portfolio
- paper trading
- backtest/research
- service health

Existing independent execution/reconciliation logic in zDash is migration-source code. It must not become a second production execution authority after parity with zksato.

Live-money authority remains outside zDash.

Explicit exclusion: `cvsz/zsme` is out of scope.
