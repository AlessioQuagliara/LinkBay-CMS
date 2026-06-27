import { apiClient } from './client'
import type {
  CartItemResponse,
  CartMeta,
  CartResponse,
  CartSession,
  DiscountResult,
} from '@/storefront/lib/types/cart'

export async function createOrFetchCart(
  sessionId: string,
  customerId?: number,
): Promise<CartResponse> {
  const { data } = await apiClient.post<CartResponse>('/api/store/cart', {
    session_id: sessionId,
    customer_id: customerId,
  })
  return data
}

export async function fetchCart(sessionId: string): Promise<CartResponse> {
  const { data } = await apiClient.get<CartResponse>(
    `/api/store/cart/${sessionId}`,
  )
  return data
}

export async function addCartItem(
  sessionId: string,
  productId: number,
  quantity: number,
  variantId?: number,
): Promise<CartItemResponse> {
  const { data } = await apiClient.post<CartItemResponse>(
    `/api/store/cart/${sessionId}/items`,
    { product_id: productId, quantity, variant_id: variantId ?? null },
  )
  return data
}

export async function updateCartItem(
  sessionId: string,
  itemId: number,
  quantity: number,
): Promise<CartItemResponse> {
  const { data } = await apiClient.patch<CartItemResponse>(
    `/api/store/cart/${sessionId}/items/${itemId}`,
    { quantity },
  )
  return data
}

export async function removeCartItem(
  sessionId: string,
  itemId: number,
): Promise<{ data: null; meta: CartMeta }> {
  const { data } = await apiClient.delete<{ data: null; meta: CartMeta }>(
    `/api/store/cart/${sessionId}/items/${itemId}`,
  )
  return data
}

export async function applyDiscount(
  sessionId: string,
  code: string,
): Promise<DiscountResult> {
  const { data } = await apiClient.post<DiscountResult>(
    `/api/store/cart/${sessionId}/discount`,
    { code },
  )
  return data
}

export function generateSessionId(): string {
  return crypto.randomUUID()
}
