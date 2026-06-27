import type { Metadata } from 'next'
import { Inter, Playfair_Display } from 'next/font/google'
import BrandThemeProvider from '@/storefront/components/layout/BrandThemeProvider'
import StoreHeader from '@/storefront/components/layout/StoreHeader'
import StoreFooter from '@/storefront/components/layout/StoreFooter'

const inter = Inter({ subsets: ['latin'], variable: '--font-inter', display: 'swap' })
const playfair = Playfair_Display({
  subsets: ['latin'],
  variable: '--font-playfair',
  display: 'swap',
})

export const metadata: Metadata = {
  robots: { index: true, follow: true },
}

export default function StorefrontLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <div
      className={`${inter.variable} ${playfair.variable} min-h-screen font-[var(--font-body,var(--font-inter))] antialiased`}
    >
      <BrandThemeProvider>
        <StoreHeader />
        <main id="main-content" tabIndex={-1}>
          {children}
        </main>
        <StoreFooter />
      </BrandThemeProvider>
    </div>
  )
}
