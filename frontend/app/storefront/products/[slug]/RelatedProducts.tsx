import type { Product } from '@/storefront/lib/types/product'
import ProductGrid from '@/storefront/components/products/ProductGrid'

interface Props {
  categorySlug: string
  excludeId: number
  tenantSlug: string
}

export default async function RelatedProducts({ categorySlug, excludeId, tenantSlug }: Props) {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL?.replace('{slug}', tenantSlug) ?? ''
  const res = await fetch(
    `${base}/api/store/categories/${categorySlug}/products?per_page=4`,
    { next: { revalidate: 60 }, headers: { 'X-Tenant-Slug': tenantSlug } },
  )

  if (!res.ok) return null

  const json = (await res.json()) as { data: Product[] }
  const related = json.data.filter((p) => p.id !== excludeId).slice(0, 4)

  if (related.length === 0) return null

  return (
    <section className="mt-16">
      <h2 className="mb-6 text-xl font-bold text-gray-900">Prodotti correlati</h2>
      <ProductGrid products={related} />
    </section>
  )
}
