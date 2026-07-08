<?php

declare(strict_types=1);

namespace Tests;

use Closure;

/**
 * Proves *physical* DB-per-tenant isolation instead of assuming it.
 *
 * Stancl's DatabaseTenancyBootstrapper isolates tenants by reconfiguring a
 * connection and pointing `database.default` at it (see
 * TenantProvisioningService::initializeDatabase()). This base class
 * reproduces that mechanism with two independent named SQLite in-memory
 * connections, each fully migrated with the tenant schema, so tests can
 * assert that data created under one tenant is genuinely unreachable from
 * the other — not just filtered out by a query scope.
 *
 * This does not exercise the domain-resolution HTTP path (InitializeTenancyByDomain)
 * or Stancl's tenancy() container bindings — see tests/Concerns/InteractsWithTenantRoutes
 * for why HTTP feature tests bypass that middleware instead of wiring real
 * central Tenant/Domain records.
 */
abstract class TenantIsolationTestCase extends TestCase
{
    /** @var array<int, string> */
    protected array $tenantConnections = [];

    protected function defineTenantConnection(string $name): void
    {
        config(["database.connections.{$name}" => [
            'driver' => 'sqlite',
            'database' => ':memory:',
            'prefix' => '',
            'foreign_key_constraints' => true,
        ]]);

        $this->artisan('migrate', [
            '--database' => $name,
            '--path' => 'database/migrations/tenant',
            '--realpath' => false,
            '--force' => true,
        ]);

        $this->tenantConnections[] = $name;
    }

    /**
     * Run $callback with the given tenant connection as the Eloquent default,
     * so models with no explicit $connection (all App\Models\Tenant\* models)
     * transparently read/write the correct tenant's physical database.
     */
    protected function asTenant(string $name, Closure $callback): mixed
    {
        $previous = config('database.default');
        config(['database.default' => $name]);

        try {
            return $callback();
        } finally {
            config(['database.default' => $previous]);
        }
    }
}
