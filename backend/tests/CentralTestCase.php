<?php

declare(strict_types=1);

namespace Tests;

use Illuminate\Foundation\Testing\RefreshDatabase;

/**
 * Base per test che usano le tabelle del central DB.
 * In test environment la connessione 'central' è redirecta su SQLite in-memory.
 */
abstract class CentralTestCase extends TestCase
{
    use RefreshDatabase;

    /**
     * Run migrations with --database=central so that:
     *  - Migrations without an explicit $connection (e.g. create_tenants_table) still
     *    land in central (not the default sqlite connection).
     *  - Migrations that use Schema::connection('central') (e.g. create_agencies_table)
     *    find the base tables they reference already created.
     *  - All migrations run in timestamp order, which is the correct dependency order.
     */
    protected function migrateFreshUsing(): array
    {
        return ['--database' => 'central'];
    }

    /**
     * Wrap each test in a transaction on the central connection so data does
     * not bleed between test methods.
     */
    protected function connectionsToTransact(): array
    {
        return ['central'];
    }
}
