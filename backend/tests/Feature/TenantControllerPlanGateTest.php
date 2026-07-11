<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\Agency;
use App\Models\Central\AgencySubscription;
use App\Models\Central\Plan;
use App\Models\Central\Tenant;
use App\Models\Central\User as CentralUser;
use Tests\CentralTestCase;

/**
 * Covers the store-creation plan gate on the central API path
 * (POST /central/api/tenants → TenantController::store()), which must apply
 * the same StoreProvisioningGate rule as the agency wizard (CreateStore).
 *
 * Uses real SQLite tenant DB files (same mechanism as TenantProvisioningTest)
 * for the happy path, since TenantController::store() calls
 * TenantProvisioningService::provision() end-to-end.
 */
class TenantControllerPlanGateTest extends CentralTestCase
{
    private static int $seq = 0;

    /** @var list<string> */
    private array $createdTenantDbFiles = [];

    protected function tearDown(): void
    {
        foreach ($this->createdTenantDbFiles as $path) {
            if (file_exists($path)) {
                unlink($path);
            }
        }

        parent::tearDown();
    }

    private function authHeaders(): array
    {
        // Sanctum's PersonalAccessToken has no explicit $connection, so it
        // follows config('database.default'). Match production (central)
        // instead of the test env's separate default 'sqlite' connection —
        // see CentralApiAuthTest for the full explanation.
        config(['database.default' => 'central']);

        // Same class of issue, different package: stancl/tenancy's own Domain
        // model (used by TenantProvisioningService::registerDomain(), which
        // provision() calls) resolves its connection from
        // config('tenancy.database.central_connection'), which defaults to
        // env('DB_CONNECTION', 'central') — 'sqlite' in phpunit.xml, not the
        // 'central' named connection CentralTestCase actually migrates onto.
        // Production sets DB_CONNECTION=central so this never surfaces there;
        // no prior test exercised registerDomain() over real HTTP, so this
        // test-env-only mismatch was never hit before.
        config(['tenancy.database.central_connection' => 'central']);

        $user = CentralUser::create([
            'name' => 'Super Admin '.self::$seq,
            'email' => 'admin'.self::$seq.'@example.com',
            'password' => bcrypt('password'),
        ]);
        $token = $user->createToken('test')->plainTextToken;

        return ['Authorization' => "Bearer {$token}"];
    }

    private function makeAgency(): Agency
    {
        self::$seq++;

        return Agency::create([
            'name' => 'API Gate Agency '.self::$seq,
            'slug' => 'api-gate-agency-'.self::$seq,
            'brand_name' => 'API Gate Agency '.self::$seq,
            'status' => 'active',
            'billing_type' => 'monthly',
        ]);
    }

    private function makeAgencyWithActivePlan(): Agency
    {
        self::$seq++;

        $agency = $this->makeAgency();
        $plan = Plan::create([
            'name' => 'API Gate Plan '.self::$seq,
            'slug' => 'api-gate-plan-'.self::$seq,
            'price' => 49,
            'billing_interval' => 'month',
            'is_active' => true,
            'sort_order' => self::$seq,
        ]);
        $agency->update(['plan_id' => $plan->id]);

        AgencySubscription::create([
            'agency_id' => $agency->id,
            'plan_id' => $plan->id,
            'status' => 'active',
            'billing_type' => 'monthly',
        ]);

        return $agency->fresh();
    }

    public function test_agency_without_active_plan_cannot_create_store_via_central_api(): void
    {
        self::$seq++;
        $agency = $this->makeAgency();
        $domain = 'api-gate-blocked-'.uniqid();

        $response = $this->postJson('/central/api/tenants', [
            'name' => 'Blocked Store',
            'domain' => $domain,
            'agency_id' => $agency->id,
            'admin_email' => 'admin@blocked.test',
            'admin_password' => 'password123',
        ], $this->authHeaders());

        $response->assertForbidden();
        $response->assertJson(['error' => 'active_plan_required']);

        $this->assertNull(Tenant::find($domain), 'No tenant row should be created when the plan gate blocks the request.');
        $this->assertFileDoesNotExist(database_path('tenant'.$domain));
    }

    public function test_agency_with_active_plan_can_create_store_via_central_api(): void
    {
        self::$seq++;
        $agency = $this->makeAgencyWithActivePlan();
        $domain = 'api-gate-allowed-'.uniqid();
        $this->createdTenantDbFiles[] = database_path('tenant'.$domain);

        $response = $this->postJson('/central/api/tenants', [
            'name' => 'Allowed Store',
            'domain' => $domain,
            'agency_id' => $agency->id,
            'admin_email' => 'admin@allowed.test',
            'admin_password' => 'password123',
        ], $this->authHeaders());

        $response->assertCreated();

        $tenant = Tenant::find($domain);
        $this->assertNotNull($tenant);
        $this->assertEquals($agency->id, $tenant->agency_id);
    }

    public function test_store_without_agency_id_is_not_gated(): void
    {
        // Central API allows agency-less tenants (e.g. internal/ops-created
        // stores) — no agency context means no plan to check, mirroring the
        // existing RequireFeature middleware convention of skipping the gate
        // when there's no agency in scope.
        self::$seq++;
        $domain = 'api-gate-no-agency-'.uniqid();
        $this->createdTenantDbFiles[] = database_path('tenant'.$domain);

        $response = $this->postJson('/central/api/tenants', [
            'name' => 'No Agency Store',
            'domain' => $domain,
            'admin_email' => 'admin@noagency.test',
            'admin_password' => 'password123',
        ], $this->authHeaders());

        $response->assertCreated();
    }
}
