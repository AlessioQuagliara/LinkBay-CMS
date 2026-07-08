'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import Link from 'next/link'
import { useRouter, useSearchParams } from 'next/navigation'
import { Loader2 } from 'lucide-react'
import { useBrandStore } from '@/stores/brandStore'
import { accountApi } from '@/lib/api/client'
import toast from 'react-hot-toast'

const schema = z
  .object({
    password: z.string().min(8, 'La password deve avere almeno 8 caratteri'),
    password_confirmation: z.string(),
  })
  .refine((d) => d.password === d.password_confirmation, {
    message: 'Le password non coincidono',
    path: ['password_confirmation'],
  })

type FormValues = z.infer<typeof schema>

export default function ResetPasswordPage() {
  const router = useRouter()
  const searchParams = useSearchParams()
  const brand = useBrandStore((s) => s.brand)

  const token = searchParams.get('token') ?? ''
  const email = searchParams.get('email') ?? ''

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  const onSubmit = async (data: FormValues) => {
    try {
      await accountApi.resetPassword({ token, email, ...data })
      toast.success('Password reimpostata con successo')
      router.push('/account/login')
    } catch {
      toast.error('Link non valido o scaduto. Richiedi un nuovo link.')
    }
  }

  if (!token || !email) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center px-4">
        <div className="text-center">
          <p className="text-gray-600 mb-4">Link non valido.</p>
          <Link href="/account/forgot-password" className="text-sm font-medium text-gray-900 hover:underline">
            Richiedi un nuovo link
          </Link>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <Link href="/" className="text-xl font-bold text-gray-900">
            {brand?.name ?? 'Store'}
          </Link>
          <p className="mt-2 text-sm text-gray-600">Crea una nuova password</p>
        </div>

        <div className="bg-white rounded-xl border border-gray-200 p-8">
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Nuova password
              </label>
              <input
                type="password"
                autoComplete="new-password"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                {...register('password')}
              />
              {errors.password && (
                <p className="mt-1 text-xs text-red-600">{errors.password.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Conferma password
              </label>
              <input
                type="password"
                autoComplete="new-password"
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                {...register('password_confirmation')}
              />
              {errors.password_confirmation && (
                <p className="mt-1 text-xs text-red-600">
                  {errors.password_confirmation.message}
                </p>
              )}
            </div>

            <button
              type="submit"
              disabled={isSubmitting}
              className="w-full flex items-center justify-center gap-2 rounded-lg bg-gray-900 text-white px-4 py-2.5 text-sm font-semibold hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
              Reimposta password
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}
