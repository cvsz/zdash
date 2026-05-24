export default function EnvBadge() {
  const env = (import.meta.env.VITE_APP_ENV || 'development').toLowerCase()
  const color = env === 'production' ? 'bg-rose-700' : env === 'staging' ? 'bg-amber-600' : 'bg-sky-700'
  return <span className={`rounded px-2 py-1 text-xs font-semibold ${color}`}>{env}</span>
}
