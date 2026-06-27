export type OrderStatus =
  | 'pending'
  | 'confirmed'
  | 'processing'
  | 'shipped'
  | 'delivered'
  | 'cancelled'
  | 'refunded'

export interface Address {
  first_name: string
  last_name: string
  address_line_1: string
  address_line_2?: string
  city: string
  postal_code: string
  country: string
  phone?: string
}

export interface OrderItem {
  id: number
  product_id: number
  name: string
  sku: string | null
  quantity: number
  price: number
  total: number
  metadata: Record<string, unknown> | null
}

export interface Order {
  id: number
  status: OrderStatus
  subtotal: number
  shipping_total: number
  discount_total: number
  total: number
  shipping_address: Address
  billing_address: Address
  shipping_method_id: number | null
  discount_code_id: number | null
  payment_method: string | null
  payment_status: string
  tracking_number: string | null
  notes: string | null
  items: OrderItem[]
  created_at: string
  updated_at: string
}

export interface CheckoutSession {
  id: number
  cart_session_id: number
  customer_id: number | null
  status: 'pending' | 'processing' | 'completed' | 'abandoned'
  shipping_address: Address | null
  billing_address: Address | null
  shipping_method_id: number | null
  discount_code_id: number | null
  subtotal: number
  shipping_amount: number
  discount_amount: number
  tax_amount: number
  total: number
  stripe_payment_intent_id: string | null
  stripe_payment_status: string | null
  completed_at: string | null
}

export interface ShippingMethod {
  id: number
  name: string
  carrier: string | null
  price: number
  estimated_days: number | null
  is_active: boolean
}
