import { defineConfig, devices } from '@playwright/test'

/**
 * E2E golden-path suite against the real local Docker stack (compose.yaml +
 * compose.override.local.yml) — no dev server is started by Playwright itself,
 * this always talks to whatever is already running. See
 * docs/local-full-flow-testing.md § "Playwright golden path" before running.
 *
 * baseURL points at a dedicated, fixed e2e test tenant (e2e-test), provisioned
 * idempotently by e2e/setup/provision-tenant.ts (globalSetup below) using the
 * same TenantProvisioningService path verified live in Docker — see
 * docs/demo-runbook.md § 0. Requires two /etc/hosts entries this repo cannot
 * add for you (see docs) — globalSetup fails fast with a clear message if
 * they're missing rather than an opaque navigation timeout.
 */
export default defineConfig({
  testDir: './e2e',
  globalSetup: './e2e/setup/provision-tenant.ts',
  fullyParallel: false, // single shared tenant/cart-session model — keep tests serial
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  workers: 1,
  timeout: 45_000,
  expect: { timeout: 10_000 },
  reporter: process.env.CI ? [['html', { open: 'never' }], ['list']] : 'list',

  use: {
    baseURL: process.env.PLAYWRIGHT_BASE_URL ?? 'http://e2e-test.linkbay-cms.test',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 15_000,
    navigationTimeout: 20_000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
})
