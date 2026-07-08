const MAIN_DOMAIN = process.env.NEXT_PUBLIC_MAIN_DOMAIN ?? 'linkbay-cms.com'

/** Extract the tenant slug from a hostname (browser or server). */
export function extractTenantSlug(hostname: string): string | null {
  const host = hostname.split(':')[0]

  if (host === MAIN_DOMAIN || host === `www.${MAIN_DOMAIN}`) return null

  if (host.endsWith(`.${MAIN_DOMAIN}`)) {
    const sub = host.slice(0, host.length - MAIN_DOMAIN.length - 1)
    return sub && sub !== 'www' ? sub : null
  }

  return null
}

/** Get the tenant slug in a client-side context. */
export function getClientTenantSlug(): string | null {
  if (typeof window === 'undefined') return null
  return extractTenantSlug(window.location.hostname)
}

/**
 * Build the tenant API base URL by substituting the `{slug}` placeholder in
 * NEXT_PUBLIC_API_BASE_URL (e.g. `https://{slug}.yoursite-linkbay-cms.com`)
 * with the resolved tenant slug. Matches the tenant's real domain on the
 * Laravel backend (see TenantProvisioningService::registerDomain).
 */
export function tenantApiUrl(slug: string): string {
  const base = process.env.NEXT_PUBLIC_API_BASE_URL ?? ''
  return base.replace('{slug}', slug)
}
