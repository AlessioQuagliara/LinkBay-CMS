// ─── Brand ───────────────────────────────────────────────────────────────────

export interface BrandSettings {
  name: string
  logo_url: string | null
  favicon_url: string | null
  primary_color: string
  secondary_color: string
  font_family: string
  stripe_publishable_key: string | null
  currency: string
  language: string
  contact_email: string | null
}

// ─── Auth ─────────────────────────────────────────────────────────────────────

export interface Customer {
  id: number
  name: string
  email: string
  phone: string | null
  email_verified_at: string | null
}

export interface AuthState {
  customer: Customer | null
  token: string | null
}

// ─── Address ──────────────────────────────────────────────────────────────────

export interface Address {
  id: number
  label: string | null
  first_name: string
  last_name: string
  company: string | null
  address_line1: string
  address_line2: string | null
  city: string
  state: string | null
  postal_code: string
  country: string
  phone: string | null
  is_default: boolean
}

export type AddressInput = Omit<Address, 'id' | 'is_default'>

// ─── Product ──────────────────────────────────────────────────────────────────

export interface ProductVariant {
  id: number
  sku: string
  price: number
  compare_at_price: number | null
  stock: number
  attributes: Record<string, string>
}

export interface Product {
  id: number
  slug: string
  name: string
  description: string | null
  price: number
  compare_at_price: number | null
  images: string[]
  variants: ProductVariant[]
  in_stock: boolean
}

// ─── Cart ─────────────────────────────────────────────────────────────────────

export interface CartItem {
  id: number
  product_id: number
  variant_id: number | null
  product_name: string
  variant_label: string | null
  sku: string
  quantity: number
  unit_price: number
  total_price: number
  image_url: string | null
}

export interface Cart {
  session_id: string
  items: CartItem[]
  subtotal: number
  discount_total: number
  shipping_total: number
  total: number
  discount_code: string | null
  currency: string
}

// ─── Checkout ─────────────────────────────────────────────────────────────────

export interface ShippingMethod {
  id: number
  name: string
  description: string | null
  price: number
  estimated_days: number | null
}

export interface CheckoutSession {
  id: string
  status: 'pending' | 'payment' | 'confirmed' | 'completed'
  email: string | null
  shipping_address: Address | null
  billing_address: Address | null
  shipping_method: ShippingMethod | null
  cart: Cart
  subtotal: number
  shipping_total: number
  discount_total: number
  total: number
  currency: string
}

export interface PaymentIntentResult {
  client_secret: string
  payment_intent_id: string
}

// ─── Order ────────────────────────────────────────────────────────────────────

export interface OrderItem {
  id: number
  product_name: string
  variant_label: string | null
  sku: string
  quantity: number
  unit_price: number
  total_price: number
  image_url: string | null
}

export interface Order {
  id: number
  reference: string
  status: string
  payment_status: string
  items: OrderItem[]
  shipping_address: Address | null
  billing_address: Address | null
  shipping_method: string | null
  subtotal: number
  shipping_total: number
  discount_total: number
  total: number
  currency: string
  created_at: string
  tracking_number: string | null
}

// ─── Wishlist ─────────────────────────────────────────────────────────────────

export interface WishlistItem {
  id: number
  product_id: number
  product_name: string
  product_slug: string
  price: number
  image_url: string | null
  in_stock: boolean
  added_at: string
}

// ─── API Responses ────────────────────────────────────────────────────────────

export interface PaginatedResponse<T> {
  data: T[]
  current_page: number
  last_page: number
  per_page: number
  total: number
}

export interface ApiError {
  message: string
  errors?: Record<string, string[]>
}
