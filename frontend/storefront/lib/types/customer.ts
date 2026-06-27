import type { Address } from './order'

export interface Customer {
  id: number
  name: string
  email: string
  phone: string | null
  email_verified_at: string | null
  addresses: CustomerAddress[]
  created_at: string
}

export interface CustomerAddress extends Address {
  id: number
  is_default: boolean
}

export interface WishlistItem {
  id: number
  product_id: number
  created_at: string
}

export interface AuthTokens {
  token: string
  token_type: 'Bearer'
}

export interface LoginPayload {
  email: string
  password: string
}

export interface RegisterPayload {
  name: string
  email: string
  password: string
  password_confirmation: string
}
