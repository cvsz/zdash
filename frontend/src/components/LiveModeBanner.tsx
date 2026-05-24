export default function LiveModeBanner({ active }: { active: boolean }) {
  if (!active) return null
  return <div className="bg-rose-800 px-4 py-2 text-center text-sm font-semibold">Live mode gates are fully enabled.</div>
}
