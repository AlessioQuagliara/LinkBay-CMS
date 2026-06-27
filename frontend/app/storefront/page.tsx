import { Suspense } from 'react'
import { headers } from 'next/headers'
import BlockRenderer from '@/storefront/components/blocks/BlockRenderer'
import ProductGrid from '@/storefront/components/products/ProductGrid'
import type { CmsPage } from '@/storefront/lib/types/brand'
import type { Product } from '@/storefront/lib/types/product'

async function fetchHomePage(tenantSlug: string): Promise<CmsPage | null> {
  try {
    const base = process.env.NEXT_PUBLIC_API_BASE_URL?.replace('{slug}', tenantSlug) ?? ''
    const res = await fetch(`${base}/api/store/pages/home`, {
      next: { revalidate: 60 },
      headers: { 'X-Tenant-Slug': tenantSlug },
    })
    if (!res.ok) return null
    const json = (await res.json()) as { data: CmsPage }
    return json.data
  } catch {
    return null
  }
}

async function fetchFeaturedProducts(tenantSlug: string): Promise<Product[]> {
  try {
    const base = process.env.NEXT_PUBLIC_API_BASE_URL?.replace('{slug}', tenantSlug) ?? ''
    const res = await fetch(`${base}/api/store/products?per_page=8&sort_by=created_at&sort_dir=desc`, {
      next: { revalidate: 60 },
      headers: { 'X-Tenant-Slug': tenantSlug },
    })
    if (!res.ok) return []
    const json = (await res.json()) as { data: Product[] }
    return json.data
  } catch {
    return []
  }
}

export default async function StorefrontHomePage() {
  const headersList = await headers()
  const tenantSlug = headersList.get('x-tenant-slug') ?? ''

  const [page, featuredProducts] = await Promise.all([
    fetchHomePage(tenantSlug),
    fetchFeaturedProducts(tenantSlug),
  ])

  if (page?.blocks?.length) {
    return (
      <Suspense>
        <BlockRenderer blocks={page.blocks} />
      </Suspense>
    )
  }

  // Fallback: mostra i prodotti più recenti
  return (
    <div className="mx-auto max-w-7xl px-4 py-12 sm:px-6 lg:px-8">
      <h1 className="mb-8 text-3xl font-bold text-gray-900">I nostri prodotti</h1>
      <ProductGrid products={featuredProducts} />
    </div>
  )
}
