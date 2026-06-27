/** Format a numeric price using the tenant currency and locale. */
export function formatPrice(
  amount: number,
  currency = 'EUR',
  locale = 'it-IT',
): string {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount)
}

/** Calculate the discount percentage between two prices. */
export function discountPercentage(original: number, sale: number): number {
  if (original <= 0) return 0
  return Math.round(((original - sale) / original) * 100)
}
