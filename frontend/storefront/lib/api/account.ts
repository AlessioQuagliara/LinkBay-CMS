import { apiClient } from './client'
import type {
  AuthTokens,
  Customer,
  CustomerAddress,
  LoginPayload,
  RegisterPayload,
  WishlistItem,
} from '@/storefront/lib/types/customer'
import type { Order } from '@/storefront/lib/types/order'

// ── Auth ──────────────────────────────────────────────────────────────────

export async function login(payload: LoginPayload): Promise<AuthTokens> {
  const { data } = await apiClient.post<{ data: AuthTokens }>(
    '/api/account/login',
    payload,
  )
  return data.data
}

export async function register(payload: RegisterPayload): Promise<AuthTokens> {
  const { data } = await apiClient.post<{ data: AuthTokens }>(
    '/api/account/register',
    payload,
  )
  return data.data
}

export async function logout(): Promise<void> {
  await apiClient.post('/api/account/logout')
}

// ── Profile ───────────────────────────────────────────────────────────────

export async function getProfile(): Promise<Customer> {
  const { data } = await apiClient.get<{ data: Customer }>('/api/account/profile')
  return data.data
}

export async function updateProfile(
  payload: Partial<Pick<Customer, 'name' | 'phone'>>,
): Promise<Customer> {
  const { data } = await apiClient.put<{ data: Customer }>(
    '/api/account/profile',
    payload,
  )
  return data.data
}

// ── Addresses ─────────────────────────────────────────────────────────────

export async function getAddresses(): Promise<CustomerAddress[]> {
  const { data } = await apiClient.get<{ data: CustomerAddress[] }>(
    '/api/account/addresses',
  )
  return data.data
}

export async function addAddress(
  address: Omit<CustomerAddress, 'id' | 'is_default'>,
): Promise<CustomerAddress> {
  const { data } = await apiClient.post<{ data: CustomerAddress }>(
    '/api/account/addresses',
    address,
  )
  return data.data
}

// ── Orders ────────────────────────────────────────────────────────────────

export async function getOrders(): Promise<Order[]> {
  const { data } = await apiClient.get<{ data: Order[] }>(
    '/api/account/orders',
  )
  return data.data
}

export async function getOrder(id: number): Promise<Order> {
  const { data } = await apiClient.get<{ data: Order }>(
    `/api/account/orders/${id}`,
  )
  return data.data
}

// ── Wishlist ──────────────────────────────────────────────────────────────

export async function getWishlist(): Promise<WishlistItem[]> {
  const { data } = await apiClient.get<{ data: WishlistItem[] }>(
    '/api/account/wishlist',
  )
  return data.data
}

export async function addToWishlist(productId: number): Promise<WishlistItem> {
  const { data } = await apiClient.post<{ data: WishlistItem }>(
    '/api/account/wishlist',
    { product_id: productId },
  )
  return data.data
}

export async function removeFromWishlist(productId: number): Promise<void> {
  await apiClient.delete(`/api/account/wishlist/${productId}`)
}
