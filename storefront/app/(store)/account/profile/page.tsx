'use client'

import { useEffect } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Loader2 } from 'lucide-react'
import { useAuthStore } from '@/stores/authStore'
import { AccountLayout } from '@/components/account/AccountLayout'
import { accountApi } from '@/lib/api/client'
import toast from 'react-hot-toast'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Profilo',
  robots: { index: false },
}

const schema = z.object({
  name: z.string().min(2, 'Almeno 2 caratteri'),
  phone: z.string().optional(),
})
type FormValues = z.infer<typeof schema>

export default function ProfilePage() {
  const customer = useAuthStore((s) => s.customer)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting, isDirty },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: { name: customer?.name ?? '', phone: customer?.phone ?? '' },
  })

  useEffect(() => {
    if (customer) {
      reset({ name: customer.name, phone: customer.phone ?? '' })
    }
  }, [customer, reset])

  const onSubmit = async (data: FormValues) => {
    try {
      await accountApi.updateProfile(data)
      toast.success('Profilo aggiornato')
    } catch {
      toast.error('Errore nell\'aggiornamento del profilo')
    }
  }

  return (
    <AccountLayout title="Il mio profilo">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-5 max-w-md" noValidate>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Email</label>
          <input
            type="email"
            value={customer?.email ?? ''}
            readOnly
            className="w-full rounded-lg border border-gray-200 px-3 py-2 text-sm bg-gray-50 text-gray-500 cursor-not-allowed"
          />
          <p className="mt-1 text-xs text-gray-400">L'email non può essere modificata</p>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Nome completo</label>
          <input
            type="text"
            autoComplete="name"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            {...register('name')}
          />
          {errors.name && <p className="mt-1 text-xs text-red-600">{errors.name.message}</p>}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Telefono</label>
          <input
            type="tel"
            autoComplete="tel"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            {...register('phone')}
          />
        </div>

        <button
          type="submit"
          disabled={isSubmitting || !isDirty}
          className="flex items-center gap-2 rounded-lg bg-gray-900 text-white px-5 py-2.5 text-sm font-semibold hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
          Salva modifiche
        </button>
      </form>
    </AccountLayout>
  )
}
