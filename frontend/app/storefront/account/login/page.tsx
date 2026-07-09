'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import toast from 'react-hot-toast'
import { getErrorMessage } from '@/storefront/lib/api/client'
import { useAuthStore } from '@/storefront/lib/store/authStore'
import { Eye, EyeOff } from 'lucide-react'

type Tab = 'login' | 'register'

const inputCls =
  'w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm placeholder-gray-400 focus:border-[var(--color-primary,#111)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary,#111)]'

function PasswordInput({
  value,
  onChange,
  placeholder,
  name,
  required,
}: {
  value: string
  onChange: (v: string) => void
  placeholder?: string
  name?: string
  required?: boolean
}) {
  const [show, setShow] = useState(false)
  return (
    <div className="relative">
      <input
        type={show ? 'text' : 'password'}
        name={name}
        required={required}
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
        className={`${inputCls} pr-11`}
        autoComplete={name === 'password' ? 'current-password' : 'new-password'}
      />
      <button
        type="button"
        onClick={() => setShow((s) => !s)}
        className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
        aria-label={show ? 'Nascondi password' : 'Mostra password'}
      >
        {show ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
      </button>
    </div>
  )
}

function LoginForm() {
  const router = useRouter()
  const { login, isLoading } = useAuthStore()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    try {
      await login({ email, password })
      toast.success('Accesso effettuato!')
      router.push('/account')
    } catch (err) {
      toast.error(getErrorMessage(err, 'Email o password non corretti.'))
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="mb-1 block text-xs font-medium text-gray-700">Email *</label>
        <input
          type="email"
          required
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="mario@esempio.it"
          className={inputCls}
        />
      </div>

      <div>
        <label className="mb-1 block text-xs font-medium text-gray-700">Password *</label>
        <PasswordInput
          name="password"
          required
          value={password}
          onChange={setPassword}
          placeholder="••••••••"
        />
      </div>

      <div className="text-right">
        <Link href="/account/forgot-password" className="text-xs text-[var(--color-primary,#111)] hover:underline">
          Password dimenticata?
        </Link>
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full rounded-xl bg-[var(--color-primary,#111)] py-3.5 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-40"
      >
        {isLoading ? 'Accesso in corso…' : 'Accedi'}
      </button>
    </form>
  )
}

function RegisterForm() {
  const router = useRouter()
  const { register, isLoading } = useAuthStore()
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirm, setConfirm] = useState('')

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (password !== confirm) {
      toast.error('Le password non coincidono.')
      return
    }
    try {
      await register({
        name,
        email,
        password,
        password_confirmation: confirm,
      })
      toast.success('Account creato con successo!')
      router.push('/account')
    } catch (err: unknown) {
      toast.error(getErrorMessage(err, 'Registrazione non riuscita.'))
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="mb-1 block text-xs font-medium text-gray-700">Nome completo *</label>
        <input
          required
          autoComplete="name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Mario Rossi"
          className={inputCls}
        />
      </div>

      <div>
        <label className="mb-1 block text-xs font-medium text-gray-700">Email *</label>
        <input
          type="email"
          required
          autoComplete="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="mario@esempio.it"
          className={inputCls}
        />
      </div>

      <div>
        <label className="mb-1 block text-xs font-medium text-gray-700">Password *</label>
        <PasswordInput
          name="password"
          required
          value={password}
          onChange={setPassword}
          placeholder="Min. 8 caratteri"
        />
      </div>

      <div>
        <label className="mb-1 block text-xs font-medium text-gray-700">Conferma password *</label>
        <PasswordInput
          name="password_confirmation"
          required
          value={confirm}
          onChange={setConfirm}
          placeholder="Ripeti la password"
        />
      </div>

      <button
        type="submit"
        disabled={isLoading}
        className="w-full rounded-xl bg-[var(--color-primary,#111)] py-3.5 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-40"
      >
        {isLoading ? 'Registrazione…' : 'Crea account'}
      </button>

      <p className="text-center text-xs text-gray-400">
        Registrandoti accetti i nostri{' '}
        <a href="/termini" className="underline">
          Termini e Condizioni
        </a>{' '}
        e la{' '}
        <a href="/privacy" className="underline">
          Privacy Policy
        </a>
        .
      </p>
    </form>
  )
}

export default function LoginPage() {
  const [tab, setTab] = useState<Tab>('login')

  return (
    <div className="flex min-h-[calc(100vh-12rem)] items-start justify-center px-4 py-16">
      <div className="w-full max-w-sm">
        <h1 className="mb-6 text-center text-2xl font-bold text-gray-900">
          {tab === 'login' ? 'Accedi' : 'Crea account'}
        </h1>

        {/* Tab switcher */}
        <div className="mb-6 flex rounded-xl border border-gray-200 bg-gray-50 p-1">
          {(['login', 'register'] as const).map((t) => (
            <button
              key={t}
              type="button"
              onClick={() => setTab(t)}
              className={`flex-1 rounded-lg py-2 text-sm font-medium transition ${
                tab === t
                  ? 'bg-white text-gray-900 shadow-sm'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              {t === 'login' ? 'Accedi' : 'Registrati'}
            </button>
          ))}
        </div>

        {tab === 'login' ? <LoginForm /> : <RegisterForm />}
      </div>
    </div>
  )
}
