export default function StatusCard({ title, value }: { title: string; value: string | number }) {
  return (
    <div className="rounded-lg border border-slate-700 bg-panel p-4 shadow">
      <p className="text-xs uppercase tracking-wider text-slate-400">{title}</p>
      <p className="mt-2 text-xl font-semibold text-accent">{value}</p>
    </div>
  )
}
