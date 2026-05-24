import { ReactNode } from 'react'

export default function RoleGate({ role, allow, children }: { role: string; allow: string[]; children: ReactNode }) {
  if (!allow.includes(role)) return null
  return <>{children}</>
}
