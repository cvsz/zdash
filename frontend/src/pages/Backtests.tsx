import { useState } from 'react'
import { apiPost } from '../api/client'

export default function Backtests() {
  const [result, setResult] = useState<Record<string, unknown> | null>(null)
  async function run() {
    const data = await apiPost<{ result: Record<string, unknown> }, object>(
      '/api/backtesting/run',
      { strategy: 'ob_aggressive', risk_per_trade: 1.0 },
      { result: {} },
    )
    setResult(data.result)
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Backtest Results</h1>
      <button className="rounded bg-accent px-4 py-2 font-semibold text-slate-900" onClick={run}>
        Run Backtest
      </button>
      <pre className="overflow-auto rounded border border-slate-700 bg-black/40 p-3 text-xs">{JSON.stringify(result, null, 2)}</pre>
    </div>
  )
}
