export interface ProductImage {
  id: number
  url: string
  alt_text: string | null
  is_primary: boolean
  sort_order: number
}

export interface ProductVariant {
  id: number
  name: string
  sku: string | null
  price: number
  quantity: number
  options: Record<string, string>
}

export interface Category {
  id: number
  name: string
  slug: string
  description: string | null
  image_url: string | null
  children: Category[]
}

export interface Product {
  id: number
  name: string
  slug: string
  description: string | null
  price: number
  compare_price: number | null
  compare_at_price: number | null
  sku: string | null
  quantity: number
  stock: number
  track_quantity: boolean
  requires_shipping: boolean
  is_active: boolean
  images: ProductImage[]
  productImages?: ProductImage[]
  categories: Category[]
  variants: ProductVariant[]
  collection_id: number | null
  seo_title: string | null
  seo_description: string | null
  seo_keywords: string | null
  created_at: string
  updated_at: string
}

export interface PaginatedResponse<T> {
  data: T[]
  meta: {
    total: number
    per_page: number
    current_page: number
    last_page: number
  }
}

export interface ProductListParams {
  page?: number
  per_page?: number
  search?: string
  category?: string
  collection_id?: number
  min_price?: number
  max_price?: number
  sort_by?: 'created_at' | 'price' | 'name'
  sort_dir?: 'asc' | 'desc'
}
