import { Suspense } from 'react'
import { notFound } from 'next/navigation'
import type { Metadata } from 'next'
import { headers } from 'next/headers'
import Image from 'next/image'
import Link from 'next/link'
import type { Product } from '@/storefront/lib/types/product'
import ProductGallery from '@/storefront/components/products/ProductGallery'
import PriceDisplay from '@/storefront/components/products/PriceDisplay'
import StockBadge from '@/storefront/components/products/StockBadge'
import AddToCartButton from '@/storefront/components/products/AddToCartButton'
import RelatedProducts from './RelatedProducts'

async function fetchProduct(slug: string, tenantSlug: string): Promise<Product | null> {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL?.replace('{slug}', tenantSlug) ?? ''
  const res = await fetch(`${base}/api/store/products/${slug}`, {
    next: { revalidate: 60 },
    headers: { 'X-Tenant-Slug': tenantSlug },
  })
  if (!res.ok) return null
  const json = (await res.json()) as { data: Product }
  return json.data
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ slug: string }>
}): Promise<Metadata> {
  const { slug } = await params
  const headersList = await headers()
  const tenantSlug = headersList.get('x-tenant-slug') ?? ''
  const product = await fetchProduct(slug, tenantSlug)

  if (!product) return { title: 'Prodotto non trovato' }

  const primaryImage =
    product.productImages?.find((i) => i.is_primary) ?? product.productImages?.[0]

  return {
    title: product.seo_title ?? product.name,
    description: product.seo_description ?? undefined,
    openGraph: {
      title: product.seo_title ?? product.name,
      description: product.seo_description ?? undefined,
      images: primaryImage ? [{ url: primaryImage.url, alt: primaryImage.alt_text ?? product.name }] : [],
    },
  }
}

export default async function ProductDetailPage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const headersList = await headers()
  const tenantSlug = headersList.get('x-tenant-slug') ?? ''
  const product = await fetchProduct(slug, tenantSlug)

  if (!product || !product.is_active) notFound()

  const images = product.productImages ?? []
  const isOutOfStock = product.track_quantity && (product.quantity ?? product.stock) <= 0

  // JSON-LD structured data
  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Product',
    name: product.name,
    description: product.description ?? undefined,
    sku: product.sku ?? undefined,
    image: images.map((i) => i.url),
    offers: {
      '@type': 'Offer',
      price: product.price,
      priceCurrency: 'EUR',
      availability: isOutOfStock
        ? 'https://schema.org/OutOfStock'
        : 'https://schema.org/InStock',
    },
  }

  return (
    <>
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }}
      />

      <div className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Breadcrumb */}
        <nav aria-label="Breadcrumb" className="mb-6 flex items-center gap-2 text-sm text-gray-500">
          <Link href="/" className="hover:text-gray-900">Home</Link>
          <span>/</span>
          <Link href="/shop" className="hover:text-gray-900">Prodotti</Link>
          {product.categories[0] && (
            <>
              <span>/</span>
              <Link href={`/shop/${product.categories[0].slug}`} className="hover:text-gray-900">
                {product.categories[0].name}
              </Link>
            </>
          )}
          <span>/</span>
          <span className="text-gray-900 font-medium">{product.name}</span>
        </nav>

        <div className="grid grid-cols-1 gap-12 lg:grid-cols-2">
          {/* Gallery */}
          <Suspense
            fallback={
              <div className="aspect-square animate-pulse rounded-2xl bg-gray-100" />
            }
          >
            <ProductGallery images={images} productName={product.name} />
          </Suspense>

          {/* Info */}
          <div className="flex flex-col gap-6">
            <div>
              {product.categories.map((c) => (
                <Link
                  key={c.id}
                  href={`/shop/${c.slug}`}
                  className="mr-2 text-xs font-medium uppercase tracking-wider text-[var(--color-primary,#111)] hover:underline"
                >
                  {c.name}
                </Link>
              ))}
              <h1 className="mt-1 text-3xl font-bold text-gray-900">{product.name}</h1>
            </div>

            <PriceDisplay
              price={product.price}
              compareAtPrice={product.compare_at_price ?? product.compare_price}
              size="lg"
            />

            <StockBadge
              quantity={product.quantity ?? product.stock}
              trackQuantity={product.track_quantity}
            />

            {product.description && (
              <div
                className="prose prose-sm prose-gray max-w-none"
                dangerouslySetInnerHTML={{ __html: product.description }}
              />
            )}

            <AddToCartButton
              productId={product.id}
              outOfStock={isOutOfStock}
            />

            {product.sku && (
              <p className="text-xs text-gray-400">SKU: {product.sku}</p>
            )}
          </div>
        </div>

        {/* Related products */}
        {product.categories[0] && (
          <Suspense>
            <RelatedProducts
              categorySlug={product.categories[0].slug}
              excludeId={product.id}
              tenantSlug={tenantSlug}
            />
          </Suspense>
        )}
      </div>
    </>
  )
}
