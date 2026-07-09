<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\User as CentralUser;
use Tests\CentralTestCase;

/**
 * Proves the 'central_api' guard fix (config/auth.php): routes/central.php's
 * tenant/plan CRUD sits behind auth:central_api, not the bare 'sanctum'
 * default, which has no provider restriction — see the same fix applied
 * tenant-side in DiscountCodeAdminApiTest. A cross-model rejection test
 * (Customer/TenantUser token against a central route) isn't reproduced here:
 * CentralTestCase only migrates central tables, so a Customer token would
 * fail on a missing `customers` table rather than a clean guard rejection —
 * not a faithful simulation. The guard's explicit `provider: central_users`
 * (instead of Sanctum's default `provider: null`) is the actual fix; these
 * tests cover that legitimate access still works and unauthenticated access
 * is still rejected.
 */
class CentralApiAuthTest extends CentralTestCase
{
    public function test_index_requires_authentication(): void
    {
        $response = $this->getJson('/central/api/tenants');

        $response->assertUnauthorized();
    }

    public function test_central_user_token_authenticates(): void
    {
        // Sanctum's PersonalAccessToken model has no explicit $connection, so it
        // always reads/writes via config('database.default') — in real deploys
        // that's 'central' (compose.yaml sets DB_CONNECTION=central), but the test
        // env (phpunit.xml) defaults it to the separate 'sqlite' connection for
        // speed, which CentralTestCase never migrates. Central Sanctum tokens are
        // real and correct in production; this line makes the test env match it
        // instead of failing on a "no such table" that's specific to test config.
        config(['database.default' => 'central']);

        $user = CentralUser::create([
            'name' => 'Super Admin',
            'email' => 'admin@example.com',
            'password' => bcrypt('password'),
        ]);
        $token = $user->createToken('test')->plainTextToken;

        $response = $this->getJson('/central/api/tenants', [
            'Authorization' => "Bearer {$token}",
        ]);

        $response->assertOk();
    }
}
