import { test, expect } from '@playwright/test'
import { StorefrontPages } from './pages/storefront.page'

/**
 * Guest checkout: no account, no login — just cart -> checkout -> Stripe
 * payment -> confirmation. Covers the public, unauthenticated path
 * (GET /api/store/checkout/{checkout}/order) separately from the
 * authenticated golden path in checkout-golden-path.spec.ts, since they hit
 * genuinely different backend code paths (see CheckoutController::order()).
 */
test.describe('Guest checkout', () => {
  test('cart -> checkout -> Stripe payment -> confirmation, no account required', async ({
    page,
  }) => {
    const stores = new StorefrontPages(page)

    await test.step('add the golden-path product to the cart as a guest', async () => {
      await page.goto('/')
      await stores.addGoldenPathProductToCart()
    })

    await test.step('go to checkout via the cart drawer', async () => {
      await stores.openCartAndGoToCheckout()
    })

    await test.step('fill shipping address and select a shipping method', async () => {
      await stores.fillShippingAddress()
      await stores.selectFirstShippingMethod()
    })

    await test.step('pay with a Stripe test card and reach the confirmation page', async () => {
      await stores.payWithStripeTestCard()
      await stores.expectOrderConfirmation()
    })

    await test.step('confirmation page shows real order data, not an error state', async () => {
      // getErrorMessage()'s amber "couldn't load order" fallback (see
      // checkout/success/page.tsx) must not be showing — that's the exact
      // regression this suite exists to catch (see CheckoutController::order()).
      await expect(page.getByText(/non riusciamo a mostrare il dettaglio/)).not.toBeVisible()
      await expect(page.getByText('Prodotti ordinati')).toBeVisible()
    })
  })
})
