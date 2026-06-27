'use client'

import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Loader2 } from 'lucide-react'

const schema = z.object({
  email: z.string().email('Email non valida'),
  first_name: z.string().min(1, 'Campo obbligatorio'),
  last_name: z.string().min(1, 'Campo obbligatorio'),
  company: z.string().optional(),
  address_line1: z.string().min(1, 'Campo obbligatorio'),
  address_line2: z.string().optional(),
  city: z.string().min(1, 'Campo obbligatorio'),
  state: z.string().optional(),
  postal_code: z.string().min(1, 'Campo obbligatorio'),
  country: z.string().min(2, 'Seleziona un paese'),
  phone: z.string().optional(),
})

export type AddressFormValues = z.infer<typeof schema>

interface Props {
  defaultValues?: Partial<AddressFormValues>
  onSubmit: (data: AddressFormValues) => Promise<void>
  submitLabel?: string
}

function FieldError({ message }: { message?: string }) {
  if (!message) return null
  return <p className="mt-1 text-xs text-red-600">{message}</p>
}

export function AddressForm({ defaultValues, onSubmit, submitLabel = 'Continua' }: Props) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<AddressFormValues>({
    resolver: zodResolver(schema),
    defaultValues,
  })

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Email <span className="text-red-500">*</span>
        </label>
        <input
          type="email"
          autoComplete="email"
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
          {...register('email')}
        />
        <FieldError message={errors.email?.message} />
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Nome <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            autoComplete="given-name"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            {...register('first_name')}
          />
          <FieldError message={errors.first_name?.message} />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Cognome <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            autoComplete="family-name"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            {...register('last_name')}
          />
          <FieldError message={errors.last_name?.message} />
        </div>
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">Azienda</label>
        <input
          type="text"
          autoComplete="organization"
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
          {...register('company')}
        />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Indirizzo <span className="text-red-500">*</span>
        </label>
        <input
          type="text"
          autoComplete="address-line1"
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
          {...register('address_line1')}
        />
        <FieldError message={errors.address_line1?.message} />
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          Indirizzo (riga 2)
        </label>
        <input
          type="text"
          autoComplete="address-line2"
          className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
          {...register('address_line2')}
        />
      </div>

      <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
        <div className="col-span-2 sm:col-span-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            CAP <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            autoComplete="postal-code"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            {...register('postal_code')}
          />
          <FieldError message={errors.postal_code?.message} />
        </div>
        <div className="col-span-2 sm:col-span-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Città <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            autoComplete="address-level2"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            {...register('city')}
          />
          <FieldError message={errors.city?.message} />
        </div>
        <div className="col-span-2 sm:col-span-1">
          <label className="block text-sm font-medium text-gray-700 mb-1">Provincia</label>
          <input
            type="text"
            autoComplete="address-level1"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
            {...register('state')}
          />
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Paese <span className="text-red-500">*</span>
          </label>
          <select
            autoComplete="country"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent bg-white"
            {...register('country')}
          >
            <option value="">Seleziona...</option>
            <option value="IT">Italia</option>
            <option value="DE">Germania</option>
            <option value="FR">Francia</option>
            <option value="ES">Spagna</option>
            <option value="US">Stati Uniti</option>
            <option value="GB">Regno Unito</option>
          </select>
          <FieldError message={errors.country?.message} />
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
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full mt-4 flex items-center justify-center gap-2 rounded-lg bg-gray-900 text-white px-6 py-3 text-sm font-semibold hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
        {submitLabel}
      </button>
    </form>
  )
}
