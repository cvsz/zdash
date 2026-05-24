export default function OfflineBanner({ offline }: { offline: boolean }) {
  if (!offline) return null
  return <div className="bg-amber-700 px-4 py-2 text-center text-sm font-semibold">Backend appears offline. Showing fallback data.</div>
}
