import { execFileSync } from 'node:child_process'
import { lookup } from 'node:dns/promises'
import path from 'node:path'

/**
 * Playwright globalSetup — runs once before the suite. Idempotently
 * provisions a single, fixed e2e test tenant against the real Docker stack,
 * using the same TenantProvisioningService path verified live (see
 * docs/demo-runbook.md § 0): create-if-missing tenant, then always ensure a
 * shipping method + product exist so the golden path has something to buy.
 *
 * Deliberately does NOT start/stop docker compose itself (constraint: don't
 * touch Docker/Traefik structure, and CI environments may bring the stack up
 * differently) — it only checks the stack is reachable and fails fast with a
 * clear message if not, rather than letting every test time out obscurely.
 */

const REPO_ROOT = path.resolve(__dirname, '../../..')
const TENANT_ID = 'e2e-test'
const STOREFRONT_HOST = 'e2e-test.linkbay-cms.test'
const API_HOST = 'e2e-test.yoursite-linkbay-cms.test'
export const E2E_PRODUCT_SLUG = 'e2e-golden-path-product'

async function assertHostsConfigured() {
  for (const host of [STOREFRONT_HOST, API_HOST, 'app.linkbay-cms.test']) {
    try {
      await lookup(host)
    } catch {
      throw new Error(
        `\n\nPlaywright e2e setup: "${host}" does not resolve.\n` +
          'Add this line to /etc/hosts (not something this suite can do for you):\n\n' +
          `  127.0.0.1 ${STOREFRONT_HOST} ${API_HOST}\n\n` +
          'See docs/local-full-flow-testing.md § "Playwright golden path".\n',
      )
    }
  }
}

async function assertStackIsUp() {
  const url = 'http://app.linkbay-cms.test/up'
  try {
    const res = await fetch(url, { signal: AbortSignal.timeout(5_000) })
    if (!res.ok) throw new Error(`HTTP ${res.status}`)
  } catch (err) {
    throw new Error(
      `\n\nPlaywright e2e setup: ${url} is not reachable (${(err as Error).message}).\n` +
        'Start the stack first:\n\n' +
        '  docker compose -f compose.yaml -f compose.override.local.yml up -d\n\n' +
        'See docs/local-full-flow-testing.md § "Playwright golden path".\n',
    )
  }
}

/**
 * Runs a PHP snippet inside the php container via `docker compose exec`.
 * Same command shape used throughout live provisioning verification
 * (docs/demo-runbook.md § 0) — not a new pattern.
 */
function tinker(php: string): string {
  return execFileSync(
    'docker',
    [
      'compose',
      '-f',
      'compose.yaml',
      '-f',
      'compose.override.local.yml',
      'exec',
      '-T',
      'php',
      'php',
      'artisan',
      'tinker',
      '--execute',
      php,
    ],
    { cwd: REPO_ROOT, encoding: 'utf-8', timeout: 60_000 },
  )
}

function provisionTenantIfMissing() {
  const php = `
    $tenant = App\\Models\\Central\\Tenant::find('${TENANT_ID}');
    if (!$tenant) {
        $agency = App\\Models\\Central\\Agency::firstOrCreate(
            ['slug' => 'e2e-agency'],
            ['name' => 'E2E Test Agency', 'brand_name' => 'E2E Test Agency', 'status' => 'active', 'billing_type' => 'monthly']
        );
        $tenant = App\\Models\\Central\\Tenant::create(['id' => '${TENANT_ID}', 'name' => 'E2E Golden Path Store', 'agency_id' => $agency->id, 'status' => 'active']);
        app(App\\Services\\TenantProvisioningService::class)->registerDomain($tenant);
        app(App\\Services\\TenantProvisioningService::class)->initializeDatabase($tenant, 'admin@e2e-test.local');
        echo 'TENANT_CREATED';
    } else {
        echo 'TENANT_EXISTS';
    }
  `.trim()

  const out = tinker(php)
  if (!out.includes('TENANT_CREATED') && !out.includes('TENANT_EXISTS')) {
    throw new Error(`Tenant provisioning failed, unexpected tinker output:\n${out}`)
  }
}

function ensureShippingMethodAndProduct() {
  const php = `
    $tenant = App\\Models\\Central\\Tenant::find('${TENANT_ID}');
    tenancy()->initialize($tenant);
    try {
        App\\Models\\Tenant\\ShippingMethod::firstOrCreate(
            ['name' => 'E2E Standard'],
            ['carrier' => 'Test', 'price' => 4.99, 'is_active' => true, 'estimated_days' => 3]
        );
        App\\Models\\Tenant\\Product::updateOrCreate(
            ['slug' => '${E2E_PRODUCT_SLUG}'],
            ['name' => 'E2E Golden Path Product', 'description' => 'Used only by the Playwright e2e suite.', 'price' => 29.99, 'stock' => 999, 'sku' => 'E2E-GP-001', 'is_active' => true]
        );
        echo 'FIXTURES_OK';
    } finally {
        tenancy()->end();
    }
  `.trim()

  const out = tinker(php)
  if (!out.includes('FIXTURES_OK')) {
    throw new Error(`Shipping method / product fixture setup failed:\n${out}`)
  }
}

export default async function globalSetup() {
  await assertHostsConfigured()
  await assertStackIsUp()
  provisionTenantIfMissing()
  ensureShippingMethodAndProduct()
}
