'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import Link from 'next/link'
import { Loader2, CheckCircle } from 'lucide-react'
import { useState } from 'react'
import { useBrandStore } from '@/stores/brandStore'
import { accountApi } from '@/lib/api/client'
import toast from 'react-hot-toast'

const schema = z.object({
  email: z.string().email('Email non valida'),
})
type FormValues = z.infer<typeof schema>

export default function ForgotPasswordPage() {
  const brand = useBrandStore((s) => s.brand)
  const [sent, setSent] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  const onSubmit = async (data: FormValues) => {
    try {
      await accountApi.forgotPassword(data.email)
      setSent(true)
    } catch {
      toast.error('Errore nell\'invio dell\'email. Riprova.')
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <Link href="/" className="text-xl font-bold text-gray-900">
            {brand?.name ?? 'Store'}
          </Link>
          <p className="mt-2 text-sm text-gray-600">Recupera la tua password</p>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-8">
          {sent ? (
            <div className="text-center">
              <CheckCircle className="w-12 h-12 text-green-500 mx-auto mb-4" />
              <h2 className="text-base font-semibold text-gray-900 mb-2">Email inviata!</h2>
              <p className="text-sm text-gray-600 mb-6">
                Controlla la tua casella di posta. Troverai le istruzioni per reimpostare la
                password.
              </p>
              <Link
                href="/account/login"
                className="text-sm font-medium text-gray-900 hover:underline"
              >
                Torna al login
              </Link>
            </div>
          ) : (
            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
              <p className="text-sm text-gray-600 mb-4">
                Inserisci la tua email e ti invieremo un link per reimpostare la password.
              </p>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
                <input
                  type="email"
                  autoComplete="email"
                  className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                  {...register('email')}
                />
                {errors.email && (
                  <p className="mt-1 text-xs text-red-600">{errors.email.message}</p>
                )}
              </div>

              <button
                type="submit"
                disabled={isSubmitting}
                className="w-full flex items-center justify-center gap-2 rounded-lg bg-gray-900 text-white px-4 py-2.5 text-sm font-semibold hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
                Invia link di recupero
              </button>
            </form>
          )}
        </div>

        {!sent && (
          <p className="mt-4 text-center text-sm text-gray-600">
            <Link href="/account/login" className="font-medium text-gray-900 hover:underline">
              ← Torna al login
            </Link>
          </p>
        )}
      </div>
    </div>
  )
}
