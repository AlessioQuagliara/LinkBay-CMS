'use client'

import { useEffect, useState } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { Plus, X, Loader2 } from 'lucide-react'
import { AccountLayout } from '@/components/account/AccountLayout'
import { AddressCard } from '@/components/account/AddressCard'
import { accountApi } from '@/lib/api/client'
import type { Address } from '@/types'
import toast from 'react-hot-toast'

const schema = z.object({
  label: z.string().optional(),
  first_name: z.string().min(1, 'Obbligatorio'),
  last_name: z.string().min(1, 'Obbligatorio'),
  company: z.string().optional(),
  address_line1: z.string().min(1, 'Obbligatorio'),
  address_line2: z.string().optional(),
  city: z.string().min(1, 'Obbligatorio'),
  state: z.string().optional(),
  postal_code: z.string().min(1, 'Obbligatorio'),
  country: z.string().min(2, 'Seleziona un paese'),
  phone: z.string().optional(),
})
type FormValues = z.infer<typeof schema>

function FieldError({ message }: { message?: string }) {
  if (!message) return null
  return <p className="mt-1 text-xs text-red-600">{message}</p>
}

export default function AddressesPage() {
  const [addresses, setAddresses] = useState<Address[]>([])
  const [loading, setLoading] = useState(true)
  const [showForm, setShowForm] = useState(false)
  const [editing, setEditing] = useState<Address | null>(null)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<FormValues>({ resolver: zodResolver(schema) })

  const loadAddresses = async () => {
    try {
      const res = await accountApi.getAddresses()
      setAddresses(res.data)
    } catch {
      toast.error('Errore nel caricamento degli indirizzi')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { loadAddresses() }, [])

  const openNew = () => {
    reset({})
    setEditing(null)
    setShowForm(true)
  }

  const openEdit = (address: Address) => {
    reset({
      label: address.label ?? '',
      first_name: address.first_name,
      last_name: address.last_name,
      company: address.company ?? '',
      address_line1: address.address_line1,
      address_line2: address.address_line2 ?? '',
      city: address.city,
      state: address.state ?? '',
      postal_code: address.postal_code,
      country: address.country,
      phone: address.phone ?? '',
    })
    setEditing(address)
    setShowForm(true)
  }

  const onSubmit = async (data: FormValues) => {
    try {
      if (editing) {
        await accountApi.updateAddress(editing.id, data)
        toast.success('Indirizzo aggiornato')
      } else {
        await accountApi.createAddress(data)
        toast.success('Indirizzo aggiunto')
      }
      setShowForm(false)
      setEditing(null)
      loadAddresses()
    } catch {
      toast.error('Errore nel salvataggio dell\'indirizzo')
    }
  }

  const handleDelete = async (id: number) => {
    await accountApi.deleteAddress(id)
    toast.success('Indirizzo eliminato')
    setAddresses((prev) => prev.filter((a) => a.id !== id))
  }

  const handleSetDefault = async (id: number) => {
    await accountApi.setDefaultAddress(id)
    toast.success('Indirizzo principale aggiornato')
    loadAddresses()
  }

  return (
    <AccountLayout title="I miei indirizzi">
      {loading ? (
        <div className="flex justify-center py-8">
          <Loader2 className="w-6 h-6 animate-spin text-gray-400" />
        </div>
      ) : (
        <>
          {!showForm && (
            <button
              onClick={openNew}
              className="flex items-center gap-2 text-sm font-medium text-gray-900 border border-gray-300 rounded-lg px-4 py-2 hover:bg-gray-50 transition-colors mb-6"
            >
              <Plus className="w-4 h-4" />
              Aggiungi indirizzo
            </button>
          )}

          {showForm && (
            <div className="border border-gray-200 rounded-xl p-5 mb-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-sm font-semibold text-gray-900">
                  {editing ? 'Modifica indirizzo' : 'Nuovo indirizzo'}
                </h2>
                <button onClick={() => setShowForm(false)} className="text-gray-400 hover:text-gray-600">
                  <X className="w-4 h-4" />
                </button>
              </div>

              <form onSubmit={handleSubmit(onSubmit)} className="space-y-4" noValidate>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Etichetta (es. Casa, Ufficio)
                  </label>
                  <input
                    type="text"
                    className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 focus:border-transparent"
                    {...register('label')}
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Nome *</label>
                    <input type="text" className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900" {...register('first_name')} />
                    <FieldError message={errors.first_name?.message} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Cognome *</label>
                    <input type="text" className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900" {...register('last_name')} />
                    <FieldError message={errors.last_name?.message} />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Indirizzo *</label>
                  <input type="text" className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900" {...register('address_line1')} />
                  <FieldError message={errors.address_line1?.message} />
                </div>

                <div className="grid grid-cols-3 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">CAP *</label>
                    <input type="text" className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900" {...register('postal_code')} />
                    <FieldError message={errors.postal_code?.message} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Città *</label>
                    <input type="text" className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900" {...register('city')} />
                    <FieldError message={errors.city?.message} />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">Paese *</label>
                    <select className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-gray-900 bg-white" {...register('country')}>
                      <option value="">—</option>
                      <option value="IT">Italia</option>
                      <option value="DE">Germania</option>
                      <option value="FR">Francia</option>
                      <option value="ES">Spagna</option>
                      <option value="US">USA</option>
                      <option value="GB">UK</option>
                    </select>
                    <FieldError message={errors.country?.message} />
                  </div>
                </div>

                <div className="flex items-center gap-3 pt-2">
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="flex items-center gap-2 rounded-lg bg-gray-900 text-white px-4 py-2 text-sm font-semibold hover:bg-gray-700 disabled:opacity-50 transition-colors"
                  >
                    {isSubmitting && <Loader2 className="w-4 h-4 animate-spin" />}
                    {editing ? 'Aggiorna' : 'Salva'}
                  </button>
                  <button
                    type="button"
                    onClick={() => setShowForm(false)}
                    className="text-sm text-gray-500 hover:text-gray-900"
                  >
                    Annulla
                  </button>
                </div>
              </form>
            </div>
          )}

          {addresses.length === 0 ? (
            <p className="text-sm text-gray-500 py-4">Nessun indirizzo salvato.</p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {addresses.map((address) => (
                <AddressCard
                  key={address.id}
                  address={address}
                  onEdit={openEdit}
                  onDelete={handleDelete}
                  onSetDefault={handleSetDefault}
                />
              ))}
            </div>
          )}
        </>
      )}
    </AccountLayout>
  )
}
