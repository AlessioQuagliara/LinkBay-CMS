'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import toast from 'react-hot-toast'
import { useAuthStore } from '@/storefront/lib/store/authStore'
import { updateProfile, getAddresses, addAddress } from '@/storefront/lib/api/account'
import { getErrorMessage } from '@/storefront/lib/api/client'
import { useQuery, useMutation } from '@tanstack/react-query'
import { Plus, MapPin, Star } from 'lucide-react'
import type { Address } from '@/storefront/lib/types/order'

const inputCls =
  'w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm placeholder-gray-400 focus:border-[var(--color-primary,#111)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary,#111)]'

function AddAddressForm({ onSuccess }: { onSuccess: () => void }) {
  const [fields, setFields] = useState<Omit<Address, 'address_line_2' | 'phone'> & { address_line_2?: string; phone?: string }>({
    first_name: '',
    last_name: '',
    address_line_1: '',
    address_line_2: '',
    city: '',
    postal_code: '',
    country: 'IT',
    phone: '',
  })
  const [isSubmitting, setIsSubmitting] = useState(false)

  function field(key: keyof typeof fields) {
    return (e: React.ChangeEvent<HTMLInputElement>) =>
      setFields((f) => ({ ...f, [key]: e.target.value }))
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    setIsSubmitting(true)
    try {
      await addAddress(fields)
      toast.success('Indirizzo aggiunto.')
      onSuccess()
    } catch (err) {
      toast.error(getErrorMessage(err, 'Impossibile aggiungere l\'indirizzo.'))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mt-4 space-y-3 rounded-2xl border border-gray-200 bg-gray-50 p-4">
      <h3 className="text-sm font-semibold text-gray-700">Nuovo indirizzo</h3>
      <div className="grid gap-3 sm:grid-cols-2">
        <input required value={fields.first_name} onChange={field('first_name')} placeholder="Nome *" className={inputCls} />
        <input required value={fields.last_name} onChange={field('last_name')} placeholder="Cognome *" className={inputCls} />
      </div>
      <input required value={fields.address_line_1} onChange={field('address_line_1')} placeholder="Indirizzo *" className={inputCls} />
      <input value={fields.address_line_2 ?? ''} onChange={field('address_line_2')} placeholder="Interno / Scala" className={inputCls} />
      <div className="grid gap-3 sm:grid-cols-3">
        <input required value={fields.city} onChange={field('city')} placeholder="Città *" className={`${inputCls} sm:col-span-2`} />
        <input required value={fields.postal_code} onChange={field('postal_code')} placeholder="CAP *" pattern="\d{5}" className={inputCls} />
      </div>
      <input type="tel" value={fields.phone ?? ''} onChange={field('phone')} placeholder="Telefono" className={inputCls} />
      <div className="flex justify-end gap-2">
        <button type="button" onClick={onSuccess} className="rounded-xl border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-100">
          Annulla
        </button>
        <button type="submit" disabled={isSubmitting} className="rounded-xl bg-[var(--color-primary,#111)] px-4 py-2 text-sm font-semibold text-white hover:opacity-90 disabled:opacity-40">
          {isSubmitting ? 'Salvo…' : 'Aggiungi'}
        </button>
      </div>
    </form>
  )
}

export default function ProfilePage() {
  const router = useRouter()
  const { token, customer, fetchProfile } = useAuthStore()
  const [name, setName] = useState('')
  const [showAddForm, setShowAddForm] = useState(false)

  useEffect(() => {
    if (!token) {
      router.replace('/account/login')
      return
    }
    // customer arriva in modo asincrono dallo store auth (fetchProfile), non è
    // disponibile al render iniziale: va sincronizzato quando si popola.
    if (customer?.name) {
      // eslint-disable-next-line react-hooks/set-state-in-effect -- sync da store async, non calcolabile al render
      setName(customer.name)
    }
  }, [token, customer, router])

  const { data: addresses = [], refetch: refetchAddresses } = useQuery({
    queryKey: ['addresses'],
    queryFn: getAddresses,
    enabled: !!token,
  })

  const { mutate: saveProfile, isPending } = useMutation({
    mutationFn: () => updateProfile({ name }),
    onSuccess: async () => {
      await fetchProfile()
      toast.success('Profilo aggiornato.')
    },
    onError: (err) => toast.error(getErrorMessage(err, 'Impossibile aggiornare il profilo.')),
  })

  if (!token) return null

  return (
    <div className="mx-auto max-w-lg px-4 py-12 sm:px-6">
      <h1 className="mb-8 text-2xl font-bold text-gray-900">Profilo</h1>

      {/* Profile form */}
      <section className="mb-8">
        <h2 className="mb-4 text-sm font-semibold text-gray-700">Dati personali</h2>
        <div className="space-y-3">
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-500">Nome</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className={inputCls}
              placeholder="Mario Rossi"
            />
          </div>
          <div>
            <label className="mb-1 block text-xs font-medium text-gray-500">Email</label>
            <input
              disabled
              value={customer?.email ?? ''}
              className={`${inputCls} cursor-not-allowed opacity-60`}
            />
          </div>
          <button
            type="button"
            onClick={() => saveProfile()}
            disabled={isPending || name === customer?.name}
            className="w-full rounded-xl bg-[var(--color-primary,#111)] py-3 text-sm font-semibold text-white hover:opacity-90 disabled:opacity-40"
          >
            {isPending ? 'Salvataggio…' : 'Salva modifiche'}
          </button>
        </div>
      </section>

      {/* Addresses */}
      <section>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="text-sm font-semibold text-gray-700">Indirizzi salvati</h2>
          <button
            type="button"
            onClick={() => setShowAddForm((s) => !s)}
            className="flex items-center gap-1 text-xs font-medium text-[var(--color-primary,#111)] hover:underline"
          >
            <Plus className="h-3.5 w-3.5" />
            Aggiungi
          </button>
        </div>

        {showAddForm && (
          <AddAddressForm
            onSuccess={() => {
              setShowAddForm(false)
              refetchAddresses()
            }}
          />
        )}

        {addresses.length === 0 && !showAddForm && (
          <p className="rounded-xl border border-dashed border-gray-200 py-8 text-center text-sm text-gray-400">
            Nessun indirizzo salvato
          </p>
        )}

        <ul className="mt-4 space-y-3">
          {addresses.map((addr) => (
            <li
              key={addr.id}
              className="flex items-start gap-3 rounded-xl border border-gray-200 bg-white p-4"
            >
              <MapPin className="mt-0.5 h-4 w-4 shrink-0 text-gray-400" />
              <div className="flex-1 text-sm text-gray-700 leading-relaxed">
                <p className="font-medium">
                  {addr.first_name} {addr.last_name}
                  {addr.is_default && (
                    <Star className="ml-1.5 inline h-3.5 w-3.5 fill-amber-400 text-amber-400" />
                  )}
                </p>
                <p>{addr.address_line_1}{addr.address_line_2 ? `, ${addr.address_line_2}` : ''}</p>
                <p>{addr.postal_code} {addr.city}</p>
              </div>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}
