export default function BuildInfo() {
  const sha = import.meta.env.VITE_BUILD_SHA || 'local'
  const time = import.meta.env.VITE_BUILD_TIME || 'dev'
  return <div className="text-xs text-slate-400">build:{sha} · {time}</div>
}
