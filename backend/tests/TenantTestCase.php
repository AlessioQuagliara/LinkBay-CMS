<?php

declare(strict_types=1);

namespace Tests;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Foundation\Testing\RefreshDatabaseState;

/**
 * Base for tests that operate on Tenant (per-store) models.
 *
 * Runs only the migrations in database/migrations/tenant/ against the
 * default SQLite in-memory connection (the same one Tenant models use
 * when no explicit $connection is set).
 */
abstract class TenantTestCase extends TestCase
{
    use RefreshDatabase {
        refreshDatabase as protected doRefreshDatabase;
    }

    /**
     * Force re-migration when the default-connection PDO is not yet cached.
     *
     * RefreshDatabaseState::$migrated is process-wide static. If CentralTestCase
     * ran first and set it to true using central migrations, this class would
     * otherwise skip migrating the tenant schema.
     */
    public function refreshDatabase(): void
    {
        if (! isset(RefreshDatabaseState::$inMemoryConnections[config('database.default')])) {
            RefreshDatabaseState::$migrated = false;
        }

        $this->doRefreshDatabase();
    }

    protected function migrateFreshUsing(): array
    {
        return [
            '--path' => 'database/migrations/tenant',
            '--realpath' => false,
        ];
    }
}
