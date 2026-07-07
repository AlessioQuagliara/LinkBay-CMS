'use client'

import { Suspense, useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { loadStripe } from '@stripe/stripe-js'
import {
  Elements,
  PaymentElement,
  useElements,
  useStripe,
} from '@stripe/react-stripe-js'
import { useQuery } from '@tanstack/react-query'
import toast from 'react-hot-toast'
import { getShippingMethods } from '@/storefront/lib/api/shipping'
import { initiateCheckout, createPaymentIntent, confirmPayment } from '@/storefront/lib/api/checkout'
import { useCartStore } from '@/storefront/lib/store/cartStore'
import { formatPrice } from '@/storefront/lib/utils/currency'
import type { Address, ShippingMethod } from '@/storefront/lib/types/order'
import { ChevronRight, Truck, Lock } from 'lucide-react'

const stripePromise = loadStripe(process.env.NEXT_PUBLIC_STRIPE_KEY ?? '')

// ── Step indicator ─────────────────────────────────────────────────────────────

function Steps({ current }: { current: 1 | 2 | 3 }) {
  const steps = ['Indirizzo', 'Spedizione', 'Pagamento']
  return (
    <ol className="mb-8 flex items-center gap-0">
      {steps.map((label, i) => {
        const n = (i + 1) as 1 | 2 | 3
        const done = current > n
        const active = current === n
        return (
          <li key={label} className="flex items-center">
            <span
              className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-semibold transition-colors ${
                done
                  ? 'bg-[var(--color-primary,#111)] text-white'
                  : active
                    ? 'border-2 border-[var(--color-primary,#111)] text-[var(--color-primary,#111)]'
                    : 'border-2 border-gray-300 text-gray-400'
              }`}
            >
              {done ? '✓' : n}
            </span>
            <span
              className={`ml-2 text-sm font-medium ${active ? 'text-gray-900' : 'text-gray-400'}`}
            >
              {label}
            </span>
            {i < steps.length - 1 && (
              <ChevronRight className="mx-3 h-4 w-4 shrink-0 text-gray-300" />
            )}
          </li>
        )
      })}
    </ol>
  )
}

// ── Address form ───────────────────────────────────────────────────────────────

const EMPTY_ADDRESS: Address = {
  first_name: '',
  last_name: '',
  address_line_1: '',
  address_line_2: '',
  city: '',
  postal_code: '',
  country: 'IT',
  phone: '',
}

function AddressForm({
  value,
  onChange,
  onNext,
}: {
  value: Address
  onChange: (a: Address) => void
  onNext: () => void
}) {
  function field(key: keyof Address) {
    return (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) =>
      onChange({ ...value, [key]: e.target.value })
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    onNext()
  }

  const inputCls =
    'w-full rounded-xl border border-gray-200 bg-white px-4 py-3 text-sm placeholder-gray-400 transition focus:border-[var(--color-primary,#111)] focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary,#111)]'

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-700">Nome *</label>
          <input
            required
            value={value.first_name}
            onChange={field('first_name')}
            placeholder="Mario"
            className={inputCls}
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-700">Cognome *</label>
          <input
            required
            value={value.last_name}
            onChange={field('last_name')}
            placeholder="Rossi"
            className={inputCls}
          />
        </div>
      </div>

      <div>
        <label className="mb-1 block text-xs font-medium text-gray-700">Indirizzo *</label>
        <input
          required
          value={value.address_line_1}
          onChange={field('address_line_1')}
          placeholder="Via Roma 1"
          className={inputCls}
        />
      </div>

      <div>
        <label className="mb-1 block text-xs font-medium text-gray-700">Interno / Scala</label>
        <input
          value={value.address_line_2 ?? ''}
          onChange={field('address_line_2')}
          placeholder="Interno 3, Scala B"
          className={inputCls}
        />
      </div>

      <div className="grid gap-4 sm:grid-cols-3">
        <div className="sm:col-span-2">
          <label className="mb-1 block text-xs font-medium text-gray-700">Città *</label>
          <input
            required
            value={value.city}
            onChange={field('city')}
            placeholder="Roma"
            className={inputCls}
          />
        </div>
        <div>
          <label className="mb-1 block text-xs font-medium text-gray-700">CAP *</label>
          <input
            required
            value={value.postal_code}
            onChange={field('postal_code')}
            placeholder="00100"
            pattern="\d{5}"
            className={inputCls}
          />
        </div>
      </div>

      <div>
        <label className="mb-1 block text-xs font-medium text-gray-700">Telefono</label>
        <input
          type="tel"
          value={value.phone ?? ''}
          onChange={field('phone')}
          placeholder="+39 333 1234567"
          className={inputCls}
        />
      </div>

      <button
        type="submit"
        className="mt-2 w-full rounded-xl bg-[var(--color-primary,#111)] py-3.5 text-sm font-semibold text-white transition hover:opacity-90"
      >
        Continua con la spedizione
      </button>
    </form>
  )
}

// ── Shipping method step ───────────────────────────────────────────────────────

function ShippingStep({
  selected,
  onSelect,
  onNext,
  onBack,
}: {
  selected: number | null
  onSelect: (id: number) => void
  onNext: () => void
  onBack: () => void
}) {
  const { data: methods = [], isLoading } = useQuery({
    queryKey: ['shipping-methods'],
    queryFn: getShippingMethods,
    staleTime: 60_000,
  })

  return (
    <div className="space-y-4">
      {isLoading && (
        <div className="space-y-3">
          {[0, 1].map((i) => (
            <div key={i} className="h-16 animate-pulse rounded-xl bg-gray-100" />
          ))}
        </div>
      )}

      {!isLoading && methods.length === 0 && (
        <p className="text-sm text-gray-500">Nessun metodo di spedizione disponibile.</p>
      )}

      {methods.map((m: ShippingMethod) => (
        <label
          key={m.id}
          className={`flex cursor-pointer items-center gap-4 rounded-xl border p-4 transition ${
            selected === m.id
              ? 'border-[var(--color-primary,#111)] bg-[var(--color-primary,#111)]/5'
              : 'border-gray-200 hover:border-gray-400'
          }`}
        >
          <input
            type="radio"
            name="shipping"
            value={m.id}
            checked={selected === m.id}
            onChange={() => onSelect(m.id)}
            className="accent-[var(--color-primary,#111)]"
          />
          <Truck className="h-5 w-5 shrink-0 text-gray-400" />
          <div className="flex-1">
            <p className="text-sm font-medium text-gray-900">{m.name}</p>
            {m.carrier && <p className="text-xs text-gray-500">{m.carrier}</p>}
            {m.estimated_days && (
              <p className="text-xs text-gray-400">
                Consegna stimata: {m.estimated_days}{' '}
                {m.estimated_days === 1 ? 'giorno' : 'giorni'}
              </p>
            )}
          </div>
          <span className="text-sm font-semibold text-gray-900">
            {m.price === 0 ? 'Gratuita' : formatPrice(m.price)}
          </span>
        </label>
      ))}

      <div className="flex gap-3 pt-2">
        <button
          type="button"
          onClick={onBack}
          className="flex-1 rounded-xl border border-gray-300 py-3.5 text-sm font-semibold text-gray-700 transition hover:bg-gray-50"
        >
          Indietro
        </button>
        <button
          type="button"
          disabled={selected === null}
          onClick={onNext}
          className="flex-1 rounded-xl bg-[var(--color-primary,#111)] py-3.5 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-40"
        >
          Continua al pagamento
        </button>
      </div>
    </div>
  )
}

// ── Stripe payment form ────────────────────────────────────────────────────────

function PaymentForm({
  checkoutId,
  onBack,
  onSuccess,
}: {
  checkoutId: number
  onBack: () => void
  onSuccess: (orderId?: number) => void
}) {
  const stripe = useStripe()
  const elements = useElements()
  const [isProcessing, setIsProcessing] = useState(false)

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!stripe || !elements) return

    setIsProcessing(true)
    try {
      const { error, paymentIntent } = await stripe.confirmPayment({
        elements,
        redirect: 'if_required',
      })

      if (error) {
        toast.error(error.message ?? 'Pagamento non riuscito.')
        return
      }

      if (paymentIntent?.status === 'succeeded') {
        const res = await confirmPayment(checkoutId, paymentIntent.id)
        toast.success('Ordine confermato!')
        onSuccess(res.data.id)
      }
    } catch {
      toast.error('Si è verificato un errore durante il pagamento.')
    } finally {
      setIsProcessing(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="rounded-xl border border-gray-200 bg-white p-4">
        <PaymentElement
          options={{
            layout: 'tabs',
          }}
        />
      </div>

      <p className="flex items-center gap-1.5 text-xs text-gray-400">
        <Lock className="h-3.5 w-3.5" />
        Pagamento sicuro e crittografato tramite Stripe
      </p>

      <div className="flex gap-3">
        <button
          type="button"
          onClick={onBack}
          disabled={isProcessing}
          className="flex-1 rounded-xl border border-gray-300 py-3.5 text-sm font-semibold text-gray-700 transition hover:bg-gray-50 disabled:opacity-40"
        >
          Indietro
        </button>
        <button
          type="submit"
          disabled={isProcessing || !stripe}
          className="flex-1 rounded-xl bg-[var(--color-primary,#111)] py-3.5 text-sm font-semibold text-white transition hover:opacity-90 disabled:opacity-40"
        >
          {isProcessing ? 'Elaborazione…' : 'Paga ora'}
        </button>
      </div>
    </form>
  )
}

// ── Order summary sidebar ──────────────────────────────────────────────────────

function OrderSummary() {
  const { items, meta } = useCartStore()

  return (
    <div className="rounded-2xl border border-gray-200 bg-gray-50 p-6">
      <h2 className="mb-4 text-sm font-semibold text-gray-900">Riepilogo ordine</h2>

      <ul className="mb-4 space-y-3">
        {items.map((item) => (
          <li key={item.id} className="flex items-start gap-3">
            <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-gray-200 text-xs text-gray-500">
              {item.quantity}×
            </div>
            <div className="flex-1 min-w-0">
              <p className="truncate text-sm font-medium text-gray-900">{item.product?.name ?? `Prodotto #${item.product_id}`}</p>
              {item.variant_id && (
                <p className="text-xs text-gray-400">Variante #{item.variant_id}</p>
              )}
            </div>
            <span className="text-sm font-semibold text-gray-900">
              {formatPrice(item.line_total)}
            </span>
          </li>
        ))}
      </ul>

      <div className="space-y-1.5 border-t border-gray-200 pt-4 text-sm">
        <div className="flex justify-between text-gray-600">
          <span>Subtotale</span>
          <span>{formatPrice(meta.subtotal)}</span>
        </div>
        {meta.discount > 0 && (
          <div className="flex justify-between text-green-600">
            <span>Sconto</span>
            <span>-{formatPrice(meta.discount)}</span>
          </div>
        )}
        <div className="flex justify-between text-gray-600">
          <span>Spedizione</span>
          <span>{meta.shipping === 0 ? 'Da calcolare' : formatPrice(meta.shipping)}</span>
        </div>
        <div className="flex justify-between text-gray-600">
          <span>IVA 22%</span>
          <span>{formatPrice(meta.tax)}</span>
        </div>
        <div className="flex justify-between pt-2 text-base font-bold text-gray-900">
          <span>Totale</span>
          <span>{formatPrice(meta.total)}</span>
        </div>
      </div>
    </div>
  )
}

// ── Main checkout orchestrator ─────────────────────────────────────────────────

function CheckoutContent() {
  const router = useRouter()
  const { sessionId, items } = useCartStore()
  const [step, setStep] = useState<1 | 2 | 3>(1)
  const [address, setAddress] = useState<Address>(EMPTY_ADDRESS)
  const [shippingMethodId, setShippingMethodId] = useState<number | null>(null)
  const [checkoutId, setCheckoutId] = useState<number | null>(null)
  const [clientSecret, setClientSecret] = useState<string | null>(null)
  const [isInitiating, setIsInitiating] = useState(false)

  // Empty cart guard
  useEffect(() => {
    if (items.length === 0) {
      router.replace('/shop')
    }
  }, [items.length, router])

  async function goToPayment() {
    if (!sessionId || shippingMethodId === null) return
    setIsInitiating(true)
    try {
      const res = await initiateCheckout({
        cart_session_id: sessionId,
        shipping_method_id: shippingMethodId,
        shipping_address: address,
      })
      const id = res.data.id
      setCheckoutId(id)
      const { client_secret } = await createPaymentIntent(id)
      setClientSecret(client_secret)
      setStep(3)
    } catch {
      toast.error('Impossibile avviare il checkout. Riprova.')
    } finally {
      setIsInitiating(false)
    }
  }

  function handleSuccess(orderId?: number) {
    const params = new URLSearchParams()
    if (checkoutId) params.set('checkout', String(checkoutId))
    if (orderId) params.set('order', String(orderId))
    router.push(`/checkout/success?${params.toString()}`)
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <h1 className="mb-8 text-2xl font-bold text-gray-900">Checkout</h1>

      <div className="grid gap-8 lg:grid-cols-5">
        {/* Left — steps */}
        <div className="lg:col-span-3">
          <Steps current={step} />

          {step === 1 && (
            <div>
              <h2 className="mb-4 text-base font-semibold text-gray-900">Indirizzo di spedizione</h2>
              <AddressForm value={address} onChange={setAddress} onNext={() => setStep(2)} />
            </div>
          )}

          {step === 2 && (
            <div>
              <h2 className="mb-4 text-base font-semibold text-gray-900">Metodo di spedizione</h2>
              <ShippingStep
                selected={shippingMethodId}
                onSelect={setShippingMethodId}
                onBack={() => setStep(1)}
                onNext={goToPayment}
              />
              {isInitiating && (
                <p className="mt-3 text-center text-sm text-gray-400">
                  Preparazione pagamento…
                </p>
              )}
            </div>
          )}

          {step === 3 && clientSecret && checkoutId !== null && (
            <div>
              <h2 className="mb-4 text-base font-semibold text-gray-900">Pagamento</h2>
              <Elements
                stripe={stripePromise}
                options={{
                  clientSecret,
                  appearance: {
                    theme: 'stripe',
                    variables: {
                      colorPrimary: 'var(--color-primary, #111)',
                      borderRadius: '12px',
                    },
                  },
                }}
              >
                <PaymentForm
                  checkoutId={checkoutId}
                  onBack={() => setStep(2)}
                  onSuccess={handleSuccess}
                />
              </Elements>
            </div>
          )}
        </div>

        {/* Right — order summary */}
        <div className="lg:col-span-2">
          <Suspense>
            <OrderSummary />
          </Suspense>
        </div>
      </div>
    </div>
  )
}

export default function CheckoutPage() {
  return (
    <Suspense>
      <CheckoutContent />
    </Suspense>
  )
}
