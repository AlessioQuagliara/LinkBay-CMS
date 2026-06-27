import { NextRequest, NextResponse } from 'next/server'

const MAIN_DOMAIN = process.env.NEXT_PUBLIC_MAIN_DOMAIN ?? 'linkbay-cms.com'
const CUSTOM_DOMAIN_MAP: Record<string, string> = process.env.CUSTOM_DOMAIN_MAP
  ? (JSON.parse(process.env.CUSTOM_DOMAIN_MAP) as Record<string, string>)
  : {}

/** Extract tenant slug from request, or null if it's the main marketing site. */
function resolveTenantSlug(hostname: string): string | null {
  if (CUSTOM_DOMAIN_MAP[hostname]) {
    return CUSTOM_DOMAIN_MAP[hostname]
  }

  if (hostname === MAIN_DOMAIN || hostname === `www.${MAIN_DOMAIN}`) {
    return null
  }

  if (hostname.endsWith(`.${MAIN_DOMAIN}`)) {
    const sub = hostname.slice(0, hostname.length - MAIN_DOMAIN.length - 1)
    if (sub && sub !== 'www') return sub
  }

  return null
}

export function middleware(request: NextRequest) {
  const host = request.headers.get('host') ?? ''
  const hostname = host.split(':')[0]
  const { pathname } = request.nextUrl

  const tenantSlug = resolveTenantSlug(hostname)

  // ── Main marketing domain ─────────────────────────────────────────────────
  if (!tenantSlug) {
    // Block direct access to the /storefront/* internal routes
    if (pathname.startsWith('/storefront')) {
      return NextResponse.redirect(new URL('/', request.url))
    }
    return NextResponse.next()
  }

  // ── Store subdomain / custom domain ───────────────────────────────────────
  const requestHeaders = new Headers(request.headers)
  requestHeaders.set('x-tenant-slug', tenantSlug)

  // Rewrite to /storefront/* so store pages are served without leaking the prefix
  const rewriteUrl = request.nextUrl.clone()
  rewriteUrl.pathname = `/storefront${pathname === '/' ? '' : pathname}`

  return NextResponse.rewrite(rewriteUrl, {
    request: { headers: requestHeaders },
  })
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon\\.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp|ico|woff2?|ttf)).*)',
  ],
}
