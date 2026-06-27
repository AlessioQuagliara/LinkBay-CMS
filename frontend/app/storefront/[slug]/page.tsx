import { notFound } from 'next/navigation'
import type { Metadata } from 'next'
import { headers } from 'next/headers'
import BlockRenderer from '@/storefront/components/blocks/BlockRenderer'
import type { CmsPage } from '@/storefront/lib/types/brand'

async function fetchPage(slug: string, tenantSlug: string): Promise<CmsPage | null> {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL?.replace('{slug}', tenantSlug) ?? ''
  const res = await fetch(`${base}/api/store/pages/${slug}`, {
    next: { revalidate: 300 },
    headers: { 'X-Tenant-Slug': tenantSlug },
  })
  if (!res.ok) return null
  const json = (await res.json()) as { data: CmsPage }
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
  const page = await fetchPage(slug, tenantSlug)

  if (!page) return { title: 'Pagina non trovata' }

  return {
    title: page.meta_title ?? page.title,
    description: page.meta_description ?? undefined,
  }
}

export default async function CmsPage({
  params,
}: {
  params: Promise<{ slug: string }>
}) {
  const { slug } = await params
  const headersList = await headers()
  const tenantSlug = headersList.get('x-tenant-slug') ?? ''
  const page = await fetchPage(slug, tenantSlug)

  if (!page) notFound()
  if (page.visibility === 'hidden') notFound()

  if (page.visibility === 'password_protected') {
    return (
      <div className="mx-auto max-w-md px-4 py-24 text-center">
        <h1 className="mb-4 text-2xl font-bold text-gray-900">{page.title}</h1>
        <p className="mb-6 text-gray-500">
          Questa pagina è protetta da password.
        </p>
        <form className="space-y-3">
          <input
            type="password"
            placeholder="Inserisci la password"
            aria-label="Password della pagina"
            className="w-full rounded-xl border border-gray-200 px-4 py-3 text-sm focus:outline-none focus-visible:ring-2 focus-visible:ring-[var(--color-primary,#111)]"
          />
          <button
            type="submit"
            className="w-full rounded-xl bg-[var(--color-primary,#111)] py-3 text-sm font-semibold text-white hover:opacity-90"
          >
            Sblocca
          </button>
        </form>
      </div>
    )
  }

  return (
    <article>
      <BlockRenderer blocks={page.blocks} />
    </article>
  )
}
