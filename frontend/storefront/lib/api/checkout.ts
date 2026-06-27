import { apiClient } from './client'
import type { Address, CheckoutSession, Order } from '@/storefront/lib/types/order'

interface InitiateCheckoutPayload {
  cart_session_id: string
  shipping_method_id: number
  shipping_address: Address
}

export async function initiateCheckout(
  payload: InitiateCheckoutPayload,
): Promise<{ data: CheckoutSession; meta: Record<string, number> }> {
  const { data } = await apiClient.post<{
    data: CheckoutSession
    meta: Record<string, number>
  }>('/api/store/checkout', payload)
  return data
}

export async function fetchCheckout(checkoutId: number): Promise<{
  data: CheckoutSession
  meta: Record<string, number>
}> {
  const { data } = await apiClient.get(`/api/store/checkout/${checkoutId}`)
  return data
}

export async function createPaymentIntent(
  checkoutId: number,
): Promise<{ client_secret: string }> {
  const { data } = await apiClient.post<{
    data: { client_secret: string }
  }>(`/api/store/checkout/${checkoutId}/payment-intent`)
  return data.data
}

export async function confirmPayment(
  checkoutId: number,
  paymentIntentId: string,
): Promise<{ data: Order; meta: { message: string } }> {
  const { data } = await apiClient.post<{
    data: Order
    meta: { message: string }
  }>(`/api/store/checkout/${checkoutId}/confirm`, {
    payment_intent_id: paymentIntentId,
  })
  return data
}
