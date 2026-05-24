export default function LogStream({ lines }: { lines: string[] }) {
  if (!lines.length) {
    return <div className="rounded border border-slate-700 bg-panel p-3 text-slate-400">No logs yet.</div>
  }
  return (
    <div className="max-h-96 overflow-auto rounded border border-slate-700 bg-black/40 p-3 font-mono text-xs">
      {lines.map((line, idx) => (
        <div key={idx} className="border-b border-slate-800 py-1 last:border-none">
          {line}
        </div>
      ))}
    </div>
  )
}
