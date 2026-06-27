import Cookies from 'js-cookie'

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? ''

class ApiError extends Error {
  constructor(
    public readonly status: number,
    message: string,
    public readonly errors?: Record<string, string[]>,
  ) {
    super(message)
    this.name = 'ApiError'
  }
}

async function request<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const token = Cookies.get('customer_token')

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
    ...(init.headers as Record<string, string>),
  }

  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
  })

  if (res.status === 204) {
    return undefined as T
  }

  const json = await res.json().catch(() => ({}))

  if (!res.ok) {
    if (res.status === 401) {
      Cookies.remove('customer_token')
    }
    throw new ApiError(res.status, json.message ?? 'Request failed', json.errors)
  }

  return json as T
}

// ─── Store (public) ───────────────────────────────────────────────────────────

export const storeApi = {
  getBrand: () => request<{ data: import('@/types').BrandSettings }>('/api/store/brand'),

  getProducts: (params?: Record<string, string>) => {
    const qs = params ? '?' + new URLSearchParams(params).toString() : ''
    return request<{ data: import('@/types').Product[] }>(`/api/store/products${qs}`)
  },

  getProduct: (slug: string) =>
    request<{ data: import('@/types').Product }>(`/api/store/products/${slug}`),

  getCategories: () =>
    request<{ data: Array<{ id: number; name: string; slug: string }> }>('/api/store/categories'),

  // Cart
  createCart: () =>
    request<{ data: import('@/types').Cart }>('/api/store/cart', { method: 'POST' }),

  getCart: (sessionId: string) =>
    request<{ data: import('@/types').Cart }>(`/api/store/cart/${sessionId}`),

  addCartItem: (
    sessionId: string,
    body: { product_id: number; variant_id?: number; quantity: number },
  ) =>
    request<{ data: import('@/types').Cart }>(`/api/store/cart/${sessionId}/items`, {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  updateCartItem: (sessionId: string, itemId: number, quantity: number) =>
    request<{ data: import('@/types').Cart }>(
      `/api/store/cart/${sessionId}/items/${itemId}`,
      { method: 'PATCH', body: JSON.stringify({ quantity }) },
    ),

  removeCartItem: (sessionId: string, itemId: number) =>
    request<{ data: import('@/types').Cart }>(
      `/api/store/cart/${sessionId}/items/${itemId}`,
      { method: 'DELETE' },
    ),

  applyDiscount: (sessionId: string, code: string) =>
    request<{ data: import('@/types').Cart }>(`/api/store/cart/${sessionId}/discount`, {
      method: 'POST',
      body: JSON.stringify({ code }),
    }),

  // Checkout
  initiateCheckout: (body: { cart_session_id: string; email?: string }) =>
    request<{ data: import('@/types').CheckoutSession }>('/api/store/checkout', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  getCheckout: (checkoutId: string) =>
    request<{ data: import('@/types').CheckoutSession }>(`/api/store/checkout/${checkoutId}`),

  createPaymentIntent: (checkoutId: string) =>
    request<{ data: import('@/types').PaymentIntentResult }>(
      `/api/store/checkout/${checkoutId}/payment-intent`,
      { method: 'POST' },
    ),

  confirmCheckout: (checkoutId: string, body: { payment_intent_id: string }) =>
    request<{ data: { order_id: number; reference: string } }>(
      `/api/store/checkout/${checkoutId}/confirm`,
      { method: 'POST', body: JSON.stringify(body) },
    ),
}

// ─── Account (authenticated) ──────────────────────────────────────────────────

export const accountApi = {
  register: (body: {
    name: string
    email: string
    password: string
    password_confirmation: string
  }) =>
    request<{ data: import('@/types').Customer; token: string }>('/api/account/register', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  login: (body: { email: string; password: string }) =>
    request<{ data: import('@/types').Customer; token: string }>('/api/account/login', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  logout: () =>
    request<void>('/api/account/logout', { method: 'POST' }),

  forgotPassword: (email: string) =>
    request<{ message: string }>('/api/account/password/forgot', {
      method: 'POST',
      body: JSON.stringify({ email }),
    }),

  resetPassword: (body: {
    token: string
    email: string
    password: string
    password_confirmation: string
  }) =>
    request<{ message: string }>('/api/account/password/reset', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  getProfile: () =>
    request<{ data: import('@/types').Customer }>('/api/account/profile'),

  updateProfile: (body: { name?: string; phone?: string }) =>
    request<{ data: import('@/types').Customer }>('/api/account/profile', {
      method: 'PUT',
      body: JSON.stringify(body),
    }),

  getAddresses: () =>
    request<{ data: import('@/types').Address[] }>('/api/account/addresses'),

  createAddress: (body: import('@/types').AddressInput) =>
    request<{ data: import('@/types').Address }>('/api/account/addresses', {
      method: 'POST',
      body: JSON.stringify(body),
    }),

  updateAddress: (id: number, body: Partial<import('@/types').AddressInput>) =>
    request<{ data: import('@/types').Address }>(`/api/account/addresses/${id}`, {
      method: 'PUT',
      body: JSON.stringify(body),
    }),

  deleteAddress: (id: number) =>
    request<void>(`/api/account/addresses/${id}`, { method: 'DELETE' }),

  setDefaultAddress: (id: number) =>
    request<{ data: import('@/types').Address }>(`/api/account/addresses/${id}/set-default`, {
      method: 'POST',
    }),

  getOrders: () =>
    request<{ data: import('@/types').Order[] }>('/api/account/orders'),

  getOrder: (id: number) =>
    request<{ data: import('@/types').Order }>(`/api/account/orders/${id}`),

  getWishlist: () =>
    request<{ data: import('@/types').WishlistItem[] }>('/api/account/wishlist'),

  addToWishlist: (productId: number) =>
    request<{ data: import('@/types').WishlistItem }>('/api/account/wishlist', {
      method: 'POST',
      body: JSON.stringify({ product_id: productId }),
    }),

  removeFromWishlist: (productId: number) =>
    request<void>(`/api/account/wishlist/${productId}`, { method: 'DELETE' }),
}

export { ApiError }
