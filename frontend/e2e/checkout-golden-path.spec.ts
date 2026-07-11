import { test } from '@playwright/test'
import { StorefrontPages } from './pages/storefront.page'

/**
 * Golden path: shop -> cart -> checkout -> Stripe payment -> confirmation ->
 * order visible in account.
 *
 * Design note on ordering: register/login happens BEFORE checkout here, not
 * after. Guest orders are stored with customer_id = null and there is no
 * email-based "claim this guest order" logic anywhere in the app (checked
 * CustomerAuthService — registering doesn't touch prior orders). Checking
 * out as a guest and then expecting to see that order after registering
 * would require inventing new linking behavior, which is out of scope here
 * ("non cambiare la logica di checkout/ordini"). An authenticated checkout
 * is the real, existing path that produces an order visible in
 * /account/orders, and is what most returning customers actually do — see
 * guest-checkout.spec.ts for the separate, genuinely-anonymous path.
 *
 * Runs serially against one browser context so cart/session state carries
 * naturally across steps, the same way a real shopper's browser would.
 */
test.describe('Checkout golden path (authenticated)', () => {
  test('shop -> cart -> checkout -> Stripe payment -> confirmation -> order in account', async ({
    page,
  }) => {
    const stores = new StorefrontPages(page)
    // Unique per run so repeated executions never collide on "email already
    // registered" — the tenant/product fixtures are fixed and reused
    // (see e2e/setup/provision-tenant.ts), only the customer identity varies.
    const email = `e2e-${Date.now()}@example.test`
    const password = 'e2e-test-password-123'

    await test.step('register a new customer account', async () => {
      await stores.registerAccount(email, password)
    })

    await test.step('add the golden-path product to the cart', async () => {
      await stores.addGoldenPathProductToCart()
    })

    await test.step('go to checkout via the cart drawer', async () => {
      await stores.openCartAndGoToCheckout()
    })

    await test.step('fill shipping address and select a shipping method', async () => {
      await stores.fillShippingAddress()
      await stores.selectFirstShippingMethod()
    })

    let orderRef = ''
    await test.step('pay with a Stripe test card and reach the confirmation page', async () => {
      await stores.payWithStripeTestCard()
      orderRef = await stores.expectOrderConfirmation()
    })

    await test.step('the order is visible in the account order history', async () => {
      await stores.expectOrderInAccount(orderRef)
    })
  })
})
