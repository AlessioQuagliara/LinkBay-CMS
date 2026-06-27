import { apiClient } from './client'
import type {
  Category,
  PaginatedResponse,
  Product,
  ProductListParams,
} from '@/storefront/lib/types/product'

export async function getProducts(
  params: ProductListParams = {},
): Promise<PaginatedResponse<Product>> {
  const { data } = await apiClient.get<PaginatedResponse<Product>>(
    '/api/store/products',
    { params },
  )
  return data
}

export async function getProduct(slug: string): Promise<Product> {
  const { data } = await apiClient.get<{ data: Product }>(
    `/api/store/products/${slug}`,
  )
  return data.data
}

export async function getCategories(): Promise<Category[]> {
  const { data } = await apiClient.get<{ data: Category[] }>(
    '/api/store/categories',
  )
  return data.data
}

export async function getCategoryProducts(
  categorySlug: string,
  params: ProductListParams = {},
): Promise<PaginatedResponse<Product>> {
  const { data } = await apiClient.get<PaginatedResponse<Product>>(
    `/api/store/categories/${categorySlug}/products`,
    { params },
  )
  return data
}

export async function searchProducts(
  query: string,
  params: ProductListParams = {},
): Promise<PaginatedResponse<Product>> {
  return getProducts({ ...params, search: query })
}
