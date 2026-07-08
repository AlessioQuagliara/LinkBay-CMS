'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useCartStore } from '@/stores/cartStore'
import { storeApi } from '@/lib/api/client'
import { CheckoutLayout } from '@/components/checkout/CheckoutLayout'
import { AddressForm, type AddressFormValues } from '@/components/checkout/AddressForm'
import type { CheckoutSession } from '@/types'
import { Loader2 } from 'lucide-react'
import toast from 'react-hot-toast'

const CHECKOUT_KEY = 'checkout_id'

export default function CheckoutAddressPage() {
  const router = useRouter()
  const { sessionId } = useCartStore()
  const [checkout, setCheckout] = useState<CheckoutSession | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const init = async () => {
      if (!sessionId) {
        router.replace('/')
        return
      }

      const existingId = sessionStorage.getItem(CHECKOUT_KEY)
      try {
        if (existingId) {
          const res = await storeApi.getCheckout(existingId)
          if (res.data.status !== 'confirmed') {
            setCheckout(res.data)
            return
          }
        }
        const res = await storeApi.initiateCheckout({ cart_session_id: sessionId })
        sessionStorage.setItem(CHECKOUT_KEY, res.data.id)
        setCheckout(res.data)
      } catch {
        toast.error('Errore nel caricamento del checkout')
        router.replace('/')
      } finally {
        setLoading(false)
      }
    }
    init()
  }, [sessionId, router])

  const handleSubmit = async (data: AddressFormValues) => {
    if (!checkout) return
    try {
      // In a real implementation the backend would accept address update here.
      // We store address in sessionStorage to pass through checkout steps.
      sessionStorage.setItem('checkout_address', JSON.stringify(data))
      sessionStorage.setItem('checkout_email', data.email)
      router.push('/checkout/shipping')
    } catch {
      toast.error('Errore nel salvataggio dell\'indirizzo')
    }
  }

  if (loading || !checkout) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-gray-400" />
      </div>
    )
  }

  const savedAddress = (() => {
    try {
      const raw = sessionStorage.getItem('checkout_address')
      return raw ? JSON.parse(raw) : undefined
    } catch {
      return undefined
    }
  })()

  return (
    <CheckoutLayout checkout={checkout} currentStep={0} title="Indirizzo di spedizione">
      <AddressForm
        defaultValues={savedAddress ?? (checkout.shipping_address ? {
          email: checkout.email ?? '',
          first_name: checkout.shipping_address.first_name,
          last_name: checkout.shipping_address.last_name,
          company: checkout.shipping_address.company ?? '',
          address_line1: checkout.shipping_address.address_line1,
          address_line2: checkout.shipping_address.address_line2 ?? '',
          city: checkout.shipping_address.city,
          state: checkout.shipping_address.state ?? '',
          postal_code: checkout.shipping_address.postal_code,
          country: checkout.shipping_address.country,
          phone: checkout.shipping_address.phone ?? '',
        } : undefined)}
        onSubmit={handleSubmit}
      />
    </CheckoutLayout>
  )
}
