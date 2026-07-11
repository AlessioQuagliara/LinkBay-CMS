<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\Agency;
use App\Models\Central\Tenant;
use App\Models\Tenant\Collection as TenantCollection;
use App\Models\Tenant\Setting;
use App\Services\TenantProvisioningService;
use Stancl\Tenancy\Exceptions\TenantDatabaseAlreadyExistsException;
use Stancl\Tenancy\Exceptions\TenantDatabaseDoesNotExistException;
use Tests\CentralTestCase;

/**
 * Regression coverage for the tenant-provisioning race found in live testing
 * (2026-07-08): TenantProvisioningService::initializeDatabase() used to call
 * tenancy()->initialize() immediately, relying on stancl/tenancy's own async
 * TenantCreated -> CreateDatabase pipeline (TenancyServiceProvider) to have
 * already created the physical database — no ordering guarantee existed
 * between the two. That pipeline is no longer wired to TenantCreated;
 * TenantProvisioningService::ensureDatabaseProvisioned() creates + migrates
 * the database itself, synchronously, before initializing tenancy.
 *
 * Uses real SQLite files under database/ (same mechanism stancl uses in
 * production for the sqlite driver, and the same pattern already used by
 * StoreFullProvisioningTest::test_duplicate_tenant_id_slug_is_blocked) —
 * these survive test transaction rollbacks and are cleaned up in tearDown().
 */
class TenantProvisioningTest extends CentralTestCase
{
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

    private function service(): TenantProvisioningService
    {
        return app(TenantProvisioningService::class);
    }

    private function makeTenant(): Tenant
    {
        $agency = Agency::create([
            'name' => 'Provisioning Test Agency',
            'slug' => 'provisioning-test-'.uniqid(),
            'brand_name' => 'Provisioning Test Agency',
            'status' => 'active',
            'billing_type' => 'monthly',
        ]);

        $tenant = Tenant::create([
            'id' => 'provtest-'.uniqid(),
            'name' => 'Provisioning Test Store',
            'agency_id' => $agency->id,
            'status' => 'active',
        ]);

        $this->createdTenantDbFiles[] = database_path('tenant'.$tenant->id);

        return $tenant;
    }

    public function test_initialize_database_creates_and_seeds_a_fresh_tenant_without_throwing(): void
    {
        $tenant = $this->makeTenant();

        $token = $this->service()->initializeDatabase($tenant, 'admin@provtest.test');

        $this->assertNotEmpty($token, 'A password-reset token should be returned when an admin email is supplied.');
        $this->assertFileExists(database_path('tenant'.$tenant->id));
    }

    public function test_initialize_database_actually_migrates_and_seeds_the_tenant_database(): void
    {
        $tenant = $this->makeTenant();

        $this->service()->initializeDatabase($tenant, 'admin@provtest.test');

        tenancy()->initialize($tenant);
        try {
            $this->assertTrue(TenantCollection::where('slug', 'default')->exists());
            $this->assertSame('admin@provtest.test', Setting::get('admin_email'));
        } finally {
            tenancy()->end();
        }
    }

    public function test_initialize_database_does_not_throw_already_exists_on_retry(): void
    {
        $tenant = $this->makeTenant();

        // First attempt provisions the database for real.
        $this->service()->initializeDatabase($tenant, 'admin@provtest.test');

        // A retry (e.g. after a partial earlier failure, or a duplicate job
        // execution) must not blow up because the database is already there —
        // this is the exact regression this test guards against.
        $this->service()->initializeDatabase($tenant->fresh(), 'admin@provtest.test');

        $this->assertTrue(true, 'Second call completed without throwing.');
    }

    public function test_initialize_database_does_not_throw_does_not_exist_for_a_brand_new_tenant(): void
    {
        // Before the fix, calling initializeDatabase() immediately after
        // Tenant::create() (as provision() does, synchronously, in the same
        // request) would race against the async CreateDatabase pipeline and
        // throw this exception when the database wasn't created yet.
        $tenant = $this->makeTenant();

        try {
            $this->service()->initializeDatabase($tenant, 'admin@provtest.test');
        } catch (TenantDatabaseDoesNotExistException|TenantDatabaseAlreadyExistsException $e) {
            $this->fail('initializeDatabase() must not depend on an async pipeline having already run: '.$e->getMessage());
        }

        $this->assertFileExists(database_path('tenant'.$tenant->id));
    }
}
