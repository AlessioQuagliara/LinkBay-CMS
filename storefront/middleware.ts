import { NextResponse } from 'next/server'
import type { NextRequest } from 'next/server'

export function middleware(request: NextRequest) {
  const token = request.cookies.get('customer_token')?.value
  const { pathname } = request.nextUrl

  const isAccountRoute = pathname.startsWith('/account')
  const isGuestOnlyRoute =
    pathname === '/account/login' ||
    pathname === '/account/register' ||
    pathname === '/account/forgot-password' ||
    pathname.startsWith('/account/reset-password')

  if (isAccountRoute && !isGuestOnlyRoute && !token) {
    const loginUrl = new URL('/account/login', request.url)
    loginUrl.searchParams.set('redirect', pathname)
    return NextResponse.redirect(loginUrl)
  }

  if (isGuestOnlyRoute && token) {
    return NextResponse.redirect(new URL('/account', request.url))
  }

  return NextResponse.next()
}

export const config = {
  matcher: ['/account/:path*', '/checkout/:path*'],
}
