<?php

declare(strict_types=1);

namespace Tests\Concerns;

use Stancl\Tenancy\Middleware\InitializeTenancyByDomain;
use Stancl\Tenancy\Middleware\PreventAccessFromCentralDomains;

/**
 * Tenant routes (routes/tenant.php) are gated by domain-based tenancy
 * resolution, which requires a real central Tenant + Domain record and a
 * matching HTTP Host header. Feature tests here exercise the tenant schema
 * directly through TenantTestCase's single in-memory SQLite connection, so
 * there is no real domain to resolve against.
 *
 * This bypasses only the domain-resolution middleware. The route, its form
 * requests, controller, service, and DB writes all still run for real.
 */
trait InteractsWithTenantRoutes
{
    protected function bypassTenantDomainResolution(): void
    {
        $this->withoutMiddleware([
            InitializeTenancyByDomain::class,
            PreventAccessFromCentralDomains::class,
        ]);
    }
}
