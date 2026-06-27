import type { Brand } from '@/storefront/lib/types/brand'

/** Apply brand CSS custom properties to the document root. */
export function applyBrandCssVars(brand: Brand): void {
  if (typeof document === 'undefined') return

  const root = document.documentElement

  root.style.setProperty('--color-primary', brand.primary_color)
  root.style.setProperty('--color-secondary', brand.secondary_color)
  root.style.setProperty('--color-accent', brand.accent_color ?? brand.primary_color)

  if (brand.font_heading) {
    root.style.setProperty('--font-heading', brand.font_heading)
  }
  if (brand.font_body) {
    root.style.setProperty('--font-body', brand.font_body)
  }
}

/** Build an inline style object for brand-colored elements. */
export function brandStyle(brand: Brand | null): React.CSSProperties {
  if (!brand) return {}
  return {
    '--color-primary': brand.primary_color,
    '--color-secondary': brand.secondary_color,
    '--color-accent': brand.accent_color ?? brand.primary_color,
  } as React.CSSProperties
}
