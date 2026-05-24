import { FormEvent, useState } from 'react'
import { apiPostEnvelope, setSession } from '../api/client'

type LoginResponse = {
  access_token: string
  token_type: string
  role: string
  username: string
}

export default function Login() {
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('admin123')
  const [error, setError] = useState('')
  async function submit(e: FormEvent) {
    e.preventDefault()
    const res = await apiPostEnvelope<LoginResponse, { username: string; password: string }>('/api/auth/login', {
      username,
      password,
    })
    if (!res || !res.ok) {
      setError(res?.error?.message || 'Login failed')
      return
    }
    setSession(res.data.access_token, res.data.role, res.data.username)
    window.location.assign('/')
  }

  return (
    <div className="mx-auto mt-20 max-w-md rounded border border-slate-700 bg-panel p-6">
      <h1 className="mb-4 text-2xl font-bold">zDash Login</h1>
      <form className="space-y-3" onSubmit={submit}>
        <input
          className="w-full rounded bg-slate-900 p-2"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="username"
        />
        <input
          className="w-full rounded bg-slate-900 p-2"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="password"
          type="password"
        />
        <button className="w-full rounded bg-accent px-4 py-2 font-semibold text-slate-900" type="submit">
          Sign In
        </button>
        {error && <p className="text-sm text-rose-400">{error}</p>}
      </form>
    </div>
  )
}
