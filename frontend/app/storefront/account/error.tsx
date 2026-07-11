'use client'

import { useEffect } from 'react'
import Link from 'next/link'
import { AlertTriangle, RotateCcw } from 'lucide-react'

export default function AccountError({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  useEffect(() => {
    console.error('[account] errore non gestito:', error)
  }, [error])

  return (
    <div className="mx-auto flex min-h-[calc(100vh-12rem)] max-w-lg flex-col items-center justify-center px-4 py-16 text-center sm:px-6">
      <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-full bg-amber-50">
        <AlertTriangle className="h-7 w-7 text-amber-500" />
      </div>

      <h1 className="text-xl font-bold text-gray-900">
        Problema durante il caricamento dell&rsquo;account
      </h1>
      <p className="mt-2 text-sm text-gray-500">
        Non siamo riusciti a mostrare questa pagina. Riprova, oppure torna alla
        home del tuo account.
      </p>

      <div className="mt-8 flex w-full flex-col gap-3 sm:flex-row">
        <button
          type="button"
          onClick={reset}
          className="flex flex-1 items-center justify-center gap-2 rounded-xl bg-[var(--color-primary,#111)] py-3.5 text-sm font-semibold text-white transition hover:opacity-90"
        >
          <RotateCcw className="h-4 w-4" />
          Riprova
        </button>
        <Link
          href="/account"
          className="flex-1 rounded-xl border border-gray-300 py-3.5 text-center text-sm font-semibold text-gray-700 transition hover:bg-gray-50"
        >
          Torna all&rsquo;account
        </Link>
      </div>
    </div>
  )
}
