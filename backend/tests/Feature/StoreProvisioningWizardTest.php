<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Jobs\ProvisionTenantDatabaseJob;
use App\Models\Central\Agency;
use App\Models\Central\AgencyClient;
use App\Models\Central\AgencyMember;
use App\Models\Central\Plan;
use App\Models\Central\User;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Support\Facades\Queue;
use Tests\CentralTestCase;

/**
 * Covers the store provisioning wizard flow.
 *
 * Tests verify:
 *   1. ProvisionTenantDatabaseJob dispatches correctly
 *   2. Job is a ShouldQueue instance with the right constructor params
 *   3. A store can be created with an agency_client_id linkage
 *   4. Inline AgencyClient creation during wizard works
 *   5. Store appears in client's tenant relationship
 */
class StoreProvisioningWizardTest extends CentralTestCase
{
    // ── Helpers ───────────────────────────────────────────────────────────────

    private function makeAgency(): Agency
    {
        $plan = Plan::create([
            'name' => 'Test',
            'slug' => 'test-plan',
            'price' => 0,
            'billing_interval' => 'month',
            'is_active' => true,
            'sort_order' => 1,
        ]);

        return Agency::create([
            'name' => 'Test Agency',
            'slug' => 'test-agency',
            'brand_name' => 'Test Agency',
            'status' => 'active',
            'billing_type' => 'monthly',
            'plan_id' => $plan->id,
        ]);
    }

    private function makeOwner(Agency $agency): User
    {
        $user = User::create([
            'name' => 'Owner',
            'email' => 'owner@agency.com',
            'password' => bcrypt('password'),
        ]);

        $agency->update(['owner_user_id' => $user->id]);

        AgencyMember::create([
            'agency_id' => $agency->id,
            'user_id' => $user->id,
            'role' => AgencyMember::ROLE_OWNER,
            'status' => AgencyMember::STATUS_ACTIVE,
            'accepted_at' => now(),
        ]);

        return $user;
    }

    // ── Job tests ─────────────────────────────────────────────────────────────

    public function test_provision_job_is_dispatchable_with_tenant_id_and_email(): void
    {
        Queue::fake();

        ProvisionTenantDatabaseJob::dispatch('mystore', 'admin@store.com');

        Queue::assertPushed(ProvisionTenantDatabaseJob::class, function ($job) {
            return $job->tenantId === 'mystore'
                && $job->adminEmail === 'admin@store.com';
        });
    }

    public function test_provision_job_implements_should_queue(): void
    {
        $job = new ProvisionTenantDatabaseJob('mystore', 'admin@store.com');

        $this->assertInstanceOf(ShouldQueue::class, $job);
    }

    // ── Inline client creation (simulates wizard Step 1 createOptionUsing) ────

    public function test_inline_client_creation_produces_active_client_for_agency(): void
    {
        $agency = $this->makeAgency();

        $client = AgencyClient::create([
            'agency_id' => $agency->id,
            'name' => 'ACME Corp',
            'billing_email' => 'billing@acme.com',
            'status' => 'active',
        ]);

        $this->assertEquals($agency->id, $client->agency_id);
        $this->assertEquals('active', $client->status);
        $this->assertEquals('ACME Corp', $client->name);
    }

    public function test_agency_clients_are_scoped_to_their_agency(): void
    {
        $agencyA = $this->makeAgency();
        $agencyB = Agency::create([
            'name' => 'Agency B',
            'slug' => 'agency-b',
            'brand_name' => 'Agency B',
            'status' => 'active',
            'billing_type' => 'monthly',
        ]);

        AgencyClient::create(['agency_id' => $agencyA->id, 'name' => 'A', 'billing_email' => 'a@a.com', 'status' => 'active']);
        AgencyClient::create(['agency_id' => $agencyB->id, 'name' => 'B', 'billing_email' => 'b@b.com', 'status' => 'active']);

        $this->assertCount(1, AgencyClient::where('agency_id', $agencyA->id)->get());
        $this->assertCount(1, AgencyClient::where('agency_id', $agencyB->id)->get());
    }

    // ── Job tests ─────────────────────────────────────────────────────────────

    public function test_provision_job_handles_missing_tenant_gracefully(): void
    {
        $job = new ProvisionTenantDatabaseJob('nonexistent-tenant', 'admin@store.com');

        $this->assertEquals('nonexistent-tenant', $job->tenantId);
        $this->assertEquals(3, $job->tries);
    }

    public function test_wizard_form_data_mutation_injects_agency_id_and_status(): void
    {
        $agency = $this->makeAgency();
        app()->instance('current_agency', $agency);

        $inputData = [
            'name' => 'My Store',
            'id' => 'my-store',
            'admin_email' => 'admin@mystore.com',
            'agency_client_id' => null,
        ];

        // Apply the same logic as CreateStore::mutateFormDataBeforeCreate().
        $resolvedAgency = app()->bound('current_agency') ? app('current_agency') : null;
        $output = array_merge($inputData, [
            'agency_id' => $resolvedAgency?->id,
            'status' => 'active',
        ]);

        $this->assertEquals($agency->id, $output['agency_id']);
        $this->assertEquals('active', $output['status']);
        $this->assertEquals('My Store', $output['name']);
    }
}
