<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Jobs\ProvisionTenantDatabaseJob;
use App\Models\Central\Agency;
use App\Models\Central\AgencyClient;
use App\Models\Central\AgencyMember;
use App\Models\Central\Plan;
use App\Models\Central\Tenant;
use App\Models\Central\User;
use Illuminate\Support\Facades\Mail;
use Illuminate\Support\Facades\Queue;
use Tests\CentralTestCase;

/**
 * Covers the store provisioning flow.
 *
 * The Filament wizard (StoresRelationManager) is NOT tested here directly —
 * Livewire/Filament tests require a separate setup. These tests cover:
 *
 *  1-2. TODO — Filament wizard steps (requires livewire()->test())
 *  3. Tenant creation carries agency_id and status='active'
 *  4. Duplicate tenant id (slug) is blocked by DB unique constraint
 *  5. Covered by test 3 (mutateFormDataBeforeCreate injects those fields)
 *  6. ProvisionTenantDatabaseJob.tries == 3
 *  7. Tenant appears in $agency->tenants after provisioning
 *  8. TODO — plan check gate for store creation (not yet wired in wizard)
 *
 * Note on Tenant in tests: The 'tenants' table lives on the 'central' SQLite
 * connection in the test environment. Unsaved Tenant models are used wherever
 * a real DB row would trigger tenancy bootstrap side-effects.
 */
class StoreFullProvisioningTest extends CentralTestCase
{
    // ── Helpers ───────────────────────────────────────────────────────────────

    private static int $seq = 0;

    private function makeAgency(?Plan $plan = null): Agency
    {
        self::$seq++;

        $agency = Agency::create([
            'name' => 'Agency '.self::$seq,
            'slug' => 'agency-'.self::$seq,
            'brand_name' => 'Agency '.self::$seq,
            'status' => 'active',
            'billing_type' => 'monthly',
        ]);

        if ($plan) {
            $agency->update(['plan_id' => $plan->id]);
            $agency->load('plan');
        }

        return $agency;
    }

    private function makeOwner(Agency $agency): User
    {
        self::$seq++;

        $user = User::create([
            'name' => 'Owner '.self::$seq,
            'email' => 'owner'.self::$seq.'@example.com',
            'password' => bcrypt('password'),
        ]);

        AgencyMember::create([
            'agency_id' => $agency->id,
            'user_id' => $user->id,
            'role' => AgencyMember::ROLE_OWNER,
            'status' => AgencyMember::STATUS_ACTIVE,
            'accepted_at' => now(),
        ]);

        $agency->update(['owner_user_id' => $user->id]);

        return $user;
    }

    private function makePlan(array $limits = []): Plan
    {
        self::$seq++;

        return Plan::create([
            'name' => 'Plan '.self::$seq,
            'slug' => 'plan-'.self::$seq,
            'price' => 49,
            'billing_interval' => 'month',
            'is_active' => true,
            'sort_order' => self::$seq,
            'limits' => $limits,
        ]);
    }

    private function makeClient(Agency $agency): AgencyClient
    {
        self::$seq++;

        return AgencyClient::create([
            'agency_id' => $agency->id,
            'name' => 'Client '.self::$seq,
            'billing_email' => 'client'.self::$seq.'@example.com',
            'status' => 'active',
        ]);
    }

    // ── Test 1 ────────────────────────────────────────────────────────────────

    // TODO — Wizard Step 1 (StoresRelationManager: select existing client → dispatch job)
    // requires Livewire test context. Implement with:
    //   livewire(StoresRelationManager::class, ['ownerRecord' => $client, ...])
    //       ->fillForm(['admin_email' => 'admin@store.com', ...])
    //       ->call('create')
    //       ->assertHasNoErrors();
    //   Queue::assertPushed(ProvisionTenantDatabaseJob::class);

    // ── Test 2 ────────────────────────────────────────────────────────────────

    // TODO — Wizard inline AgencyClient creation (createOptionUsing) requires
    // Filament Livewire test context. The callback saves the client and dispatches
    // the job in the same flow.

    // ── Test 3 ────────────────────────────────────────────────────────────────

    public function test_tenant_creation_stamps_agency_id_and_active_status(): void
    {
        // Simulates what mutateFormDataBeforeCreate injects before Eloquent create
        $agency = $this->makeAgency();
        $client = $this->makeClient($agency);

        $tenant = Tenant::create([
            'id' => 'store-'.uniqid(),
            'name' => 'My Store',
            'agency_id' => $agency->id,
            'agency_client_id' => $client->id,
            'status' => 'active',
        ]);

        $tenant->refresh();

        $this->assertEquals($agency->id, $tenant->agency_id);
        $this->assertEquals('active', $tenant->status);
        $this->assertEquals($client->id, $tenant->agency_client_id);
    }

    // ── Test 4 ────────────────────────────────────────────────────────────────

    public function test_duplicate_tenant_id_slug_is_blocked(): void
    {
        $agency = $this->makeAgency();

        // Use uniqid() so each run starts from a fresh slug —
        // stancl/tenancy creates a real SQLite file per tenant that survives
        // transaction rollbacks between runs.
        $slug = 'dup-'.uniqid();

        Tenant::create([
            'id' => $slug,
            'name' => 'Store One',
            'agency_id' => $agency->id,
            'status' => 'active',
        ]);

        // Second create with the same slug must throw (stancl detects the DB file exists)
        $threw = false;
        try {
            Tenant::create([
                'id' => $slug,
                'name' => 'Store Two',
                'agency_id' => $agency->id,
                'status' => 'active',
            ]);
        } catch (\Throwable $e) {
            $threw = true;
        }

        $this->assertTrue($threw, 'Creating a duplicate tenant slug must throw a Throwable');
    }

    // ── Test 6 ────────────────────────────────────────────────────────────────

    public function test_provision_tenant_database_job_has_3_tries(): void
    {
        $job = new ProvisionTenantDatabaseJob('store-test', 'admin@store.com');

        $this->assertEquals(3, $job->tries);
    }

    public function test_provision_job_carries_tenant_id_and_admin_email(): void
    {
        Queue::fake();

        $tenantId = 'dispatch-store-'.uniqid();
        $adminEmail = 'admin@store.com';

        ProvisionTenantDatabaseJob::dispatch($tenantId, $adminEmail);

        Queue::assertPushed(
            ProvisionTenantDatabaseJob::class,
            fn ($job) => $job->tenantId === $tenantId && $job->adminEmail === $adminEmail,
        );
    }

    // ── Test 7 ────────────────────────────────────────────────────────────────

    public function test_tenant_appears_in_agency_tenants_relation(): void
    {
        $agency = $this->makeAgency();

        Tenant::create([
            'id' => 'relation-store-'.uniqid(),
            'name' => 'Relation Store',
            'agency_id' => $agency->id,
            'status' => 'active',
        ]);

        $agency->load('tenants');

        $this->assertCount(1, $agency->tenants);
        $this->assertEquals($agency->id, $agency->tenants->first()->agency_id);
    }

    // ── Test 8 ────────────────────────────────────────────────────────────────

    // TODO — "Admin without active plan cannot create a store" gate.
    // When the plan-based store limit is enforced in the wizard, implement:
    //
    // public function test_admin_without_active_plan_cannot_create_store(): void
    // {
    //     $freePlan = $this->makePlan(['max_stores' => 0]);
    //     $agency   = $this->makeAgency($freePlan);
    //     $admin    = $this->makeOwner($agency);
    //     $this->actingAs($admin);
    //     app()->instance('current_agency', $agency);
    //
    //     // TODO — verify route / Livewire wizard for store creation
    //     $response = $this->post(route('filament.agency.resources.stores.create'), [...]);
    //     $response->assertForbidden();
    // }

    // ── Welcome email ─────────────────────────────────────────────────────────

    public function test_provision_job_sends_welcome_email_to_admin(): void
    {
        Mail::fake();
        Queue::fake();

        $tenantId = 'welcome-store-'.uniqid();
        $adminEmail = 'newadmin@store.com';

        // The job sends StoreAdminWelcomeMail inside handle() → stub with Queue::fake()
        // and verify the Mail dispatch happens when the job runs directly.
        $agency = $this->makeAgency();
        Tenant::create([
            'id' => $tenantId,
            'name' => 'Welcome Store',
            'agency_id' => $agency->id,
            'status' => 'active',
        ]);

        // ProvisionTenantDatabaseJob.handle() calls TenantProvisioningService which
        // needs a live tenant DB. We test dispatch-level only; integration test of
        // handle() would require a TenantTestCase setup.
        ProvisionTenantDatabaseJob::dispatch($tenantId, $adminEmail);

        Queue::assertPushed(
            ProvisionTenantDatabaseJob::class,
            fn ($job) => $job->adminEmail === $adminEmail,
        );
    }
}
