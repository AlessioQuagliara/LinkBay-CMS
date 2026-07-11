import type { Page } from '@playwright/test'
import { expect } from '@playwright/test'
import { E2E_PRODUCT_SLUG } from '../setup/provision-tenant'

/**
 * Minimal Page Object Model for the golden path — one class per screen area,
 * only the actions/assertions the specs actually need. Not a full framework.
 */
export class StorefrontPages {
  constructor(private readonly page: Page) {}

  async addGoldenPathProductToCart() {
    await this.page.goto(`/products/${E2E_PRODUCT_SLUG}`)
    await this.page.getByRole('button', { name: 'Aggiungi al carrello' }).click()
    await expect(this.page.getByRole('button', { name: 'Aggiunto al carrello' })).toBeVisible()
  }

  async openCartAndGoToCheckout() {
    await this.page.getByRole('button', { name: /^Carrello/ }).click()
    await expect(this.page.getByRole('dialog', { name: 'Carrello' })).toBeVisible()
    await this.page.getByRole('link', { name: 'Vai al checkout' }).click()
    await expect(this.page).toHaveURL(/\/checkout$/)
  }

  async fillShippingAddress() {
    await this.page.getByPlaceholder('Mario').fill('Mario')
    await this.page.getByPlaceholder('Rossi').fill('Rossi')
    await this.page.getByPlaceholder('Via Roma 1').fill('Via Test 1')
    await this.page.getByPlaceholder('Roma').fill('Roma')
    await this.page.getByPlaceholder('00100').fill('00100')
    await this.page.getByRole('button', { name: 'Continua con la spedizione' }).click()
  }

  async selectFirstShippingMethod() {
    await this.page.locator('input[name="shipping"]').first().check()
    await this.page.getByRole('button', { name: 'Continua al pagamento' }).click()
    // Stripe PaymentElement mounts asynchronously once the PaymentIntent
    // client_secret comes back — give it a moment before the frame exists.
    await expect(this.page.locator('iframe[name^="__privateStripeFrame"]').first()).toBeVisible({
      timeout: 15_000,
    })
  }

  /**
   * Fills Stripe's real test-mode PaymentElement iframe with the standard
   * test card and submits. Requires NEXT_PUBLIC_STRIPE_KEY (frontend) and a
   * matching Stripe test secret key (backend) to be configured — see
   * docs/local-full-flow-testing.md § "Playwright golden path". This is the
   * one step that talks to Stripe's real test-mode servers over the network.
   */
  async payWithStripeTestCard() {
    const stripeFrame = this.page.frameLocator('iframe[name^="__privateStripeFrame"]').first()
    await stripeFrame.getByPlaceholder('1234 1234 1234 1234').fill('4242424242424242')
    await stripeFrame.getByPlaceholder('MM / YY').fill('12/34')
    await stripeFrame.getByPlaceholder('CVC').fill('123')

    const postalCode = stripeFrame.getByPlaceholder('CAP')
    if (await postalCode.isVisible().catch(() => false)) {
      await postalCode.fill('00100')
    }

    await this.page.getByRole('button', { name: 'Paga ora' }).click()
  }

  async expectOrderConfirmation(): Promise<string> {
    await expect(this.page).toHaveURL(/\/checkout\/success/, { timeout: 20_000 })
    await expect(this.page.getByRole('heading', { name: 'Ordine confermato!' })).toBeVisible()
    const orderRef = await this.page.getByText(/Ordine #\d+/).textContent()
    return orderRef ?? ''
  }

  async registerAccount(email: string, password: string) {
    await this.page.goto('/account/login')
    await this.page.getByRole('button', { name: 'Registrati' }).click()
    await this.page.getByPlaceholder('Mario Rossi').fill('E2E Test Customer')
    await this.page.getByPlaceholder('mario@esempio.it').fill(email)
    await this.page.locator('input[name="password"]').fill(password)
    await this.page.locator('input[name="password_confirmation"]').fill(password)
    await this.page.getByRole('button', { name: 'Crea account' }).click()
    await expect(this.page).toHaveURL(/\/account$/, { timeout: 15_000 })
  }

  async login(email: string, password: string) {
    await this.page.goto('/account/login')
    await this.page.locator('input[type="email"]').fill(email)
    await this.page.locator('input[name="password"]').fill(password)
    await this.page.getByRole('button', { name: 'Accedi' }).click()
    await expect(this.page).toHaveURL(/\/account$/, { timeout: 15_000 })
  }

  async expectOrderInAccount(orderRef: string) {
    await this.page.goto('/account/orders')
    await expect(this.page.getByText(orderRef)).toBeVisible({ timeout: 10_000 })
  }
}
