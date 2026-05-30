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

    protected string $connectUsing = 'central';

    protected function setUp(): void
    {
        parent::setUp();

        // Esegui le migration central su SQLite in-memory
        $this->artisan('migrate', [
            '--database' => 'central',
            '--path'     => 'database/migrations/central',
            '--force'    => true,
        ]);

        // Migration users (necessaria per FK)
        $this->artisan('migrate', [
            '--database' => 'central',
            '--path'     => 'database/migrations',
            '--force'    => true,
        ]);
    }
}
