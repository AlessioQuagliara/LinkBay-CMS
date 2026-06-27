import type { Product } from './product'

export interface CartItem {
  id: number
  cart_session_id: number
  product_id: number
  variant_id: number | null
  quantity: number
  unit_price: number
  line_total: number
  product: Product
  metadata: Record<string, unknown> | null
}

export interface CartSession {
  id: number
  session_id: string
  customer_id: number | null
  expires_at: string | null
  cartItems: CartItem[]
  metadata: Record<string, unknown> | null
}

export interface CartMeta {
  subtotal: number
  discount: number
  shipping: number
  tax: number
  total: number
}

export interface CartResponse {
  data: CartSession
  meta: CartMeta
}

export interface CartItemResponse {
  data: CartItem
  meta: CartMeta
}

export interface DiscountResult {
  data: {
    id: number
    code: string
    type: 'percentage' | 'fixed' | 'free_shipping'
    value: number
  } | null
  meta: {
    success: boolean
    message: string
  }
}
