import { apiClient } from './client'
import type { ShippingMethod } from '@/storefront/lib/types/order'

export async function getShippingMethods(): Promise<ShippingMethod[]> {
  const { data } = await apiClient.get<{ data: ShippingMethod[] }>('/api/store/shipping-methods')
  return data.data
}
