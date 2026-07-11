<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Central\Tenant;
use App\Models\Tenant\Collection;
use App\Models\Tenant\Setting;
use App\Models\Tenant\User;
use Illuminate\Support\Facades\Artisan;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Str;

class TenantProvisioningService
{
    /**
     * Full provision from scratch: creates central record + domain + initializes DB.
     * Used by the central API (TenantController) and admin panel.
     * For agency-panel store creation, use CreateStore::afterCreate() instead.
     */
    public function provision(array $data): Tenant
    {
        $tenant = Tenant::create([
            'id' => $data['domain'],
            'name' => $data['name'],
            'plan_id' => $data['plan_id'] ?? null,
            'agency_id' => $data['agency_id'] ?? null,
            'agency_client_id' => $data['agency_client_id'] ?? null,
            'status' => 'active',
        ]);

        $this->registerDomain($tenant);
        $this->initializeDatabase($tenant, $data['admin_email'] ?? null);

        return $tenant;
    }

    /**
     * Registers the full domain for an existing tenant in the domains table.
     * Idempotent — safe to call multiple times.
     */
    public function registerDomain(Tenant $tenant): void
    {
        $storeDomain = config('app.store_domain', 'yoursite-linkbay-cms.com');
        $fullDomain = $tenant->id.'.'.$storeDomain;

        if (! $tenant->domains()->where('domain', $fullDomain)->exists()) {
            $tenant->domains()->create(['domain' => $fullDomain]);
        }
    }

    /**
     * Initializes the tenant database schema and seeds defaults.
     * Can be called independently for re-provisioning or recovery.
     *
     * Returns the plaintext password-reset token when an adminEmail is provided
     * (for use in the welcome email), or null otherwise.
     */
    public function initializeDatabase(Tenant $tenant, ?string $adminEmail = null): ?string
    {
        $email = $adminEmail
            ?? (isset($tenant->admin_email) ? $tenant->admin_email : null)
            ?? 'admin@'.$tenant->id.'.test';

        $this->ensureDatabaseProvisioned($tenant);

        Log::info('TenantProvisioningService: initializing tenancy for seeding', ['tenant_id' => $tenant->id]);
        tenancy()->initialize($tenant);
        $resetToken = null;
        try {
            $resetToken = $this->seedTenantDefaults([
                'name' => $tenant->name,
                'admin_email' => $email,
            ]);
        } finally {
            // Always restore central connection, even if seeding throws.
            tenancy()->end();
        }

        // Return token only when caller supplied a real admin email.
        return ($adminEmail !== null) ? $resetToken : null;
    }

    /**
     * Creates the tenant's physical database and runs its migrations,
     * synchronously, if not already done.
     *
     * Root cause this works around: stancl/tenancy's own automatic
     * TenantCreated -> [CreateDatabase, MigrateDatabase, SeedDatabase] pipeline
     * (previously registered in TenancyServiceProvider) is dispatched async, on
     * the queue, as a side effect of Tenant::create(). This method used to call
     * tenancy()->initialize() immediately afterward — sometimes synchronously
     * within the same request (provision(), used by TenantController), sometimes
     * from a second, independently-queued job (ProvisionTenantDatabaseJob, used
     * by the agency wizard) — with no ordering guarantee against that pipeline.
     * DatabaseTenancyBootstrapper::bootstrap() throws
     * TenantDatabaseDoesNotExistException in local env if the database isn't
     * there yet, which is exactly what live testing hit. Confirmed live: the
     * pipeline's own SeedDatabase step also ran database/seeders/TenantSeeder.php
     * (unrelated demo-data seeder, never wired to anything else in this app),
     * duplicating/conflicting with seedTenantDefaults() below.
     *
     * Fix: make this method the single, synchronous source of truth for
     * "does this tenant have a working database" — create it here if missing,
     * migrate it here, every time, idempotently. TenancyServiceProvider no
     * longer registers the automatic pipeline for TenantCreated (still does for
     * TenantDeleted — DeleteDatabase has no app-specific equivalent to race
     * against). Whichever caller runs this (provision(), ProvisionTenantDatabaseJob)
     * still decides sync vs. async — this method itself just no longer races
     * against a second, independent process doing the same job.
     */
    private function ensureDatabaseProvisioned(Tenant $tenant): void
    {
        $tenant->database()->makeCredentials();
        $manager = $tenant->database()->manager();
        $databaseName = $tenant->database()->getName();

        Log::info('TenantProvisioningService: checking tenant database existence', [
            'tenant_id' => $tenant->id,
            'database' => $databaseName,
        ]);

        if (! $manager->databaseExists($databaseName)) {
            Log::info('TenantProvisioningService: creating tenant database', [
                'tenant_id' => $tenant->id,
                'database' => $databaseName,
            ]);
            $manager->createDatabase($tenant);
        } else {
            Log::info('TenantProvisioningService: tenant database already exists, skipping create', [
                'tenant_id' => $tenant->id,
                'database' => $databaseName,
            ]);
        }

        Log::info('TenantProvisioningService: running tenant migrations', ['tenant_id' => $tenant->id]);
        Artisan::call('tenants:migrate', ['--tenants' => [$tenant->getTenantKey()]]);
    }

    public function deprovision(Tenant $tenant): void
    {
        $tenant->delete();
    }

    /**
     * Seeds initial data into the tenant database while tenancy is active.
     * Creates the admin user and generates a password-reset token.
     *
     * Idempotent by design — a retry of initializeDatabase() for a tenant that
     * was already (partially or fully) seeded must not throw a unique
     * constraint violation. firstOrCreate/updateOrInsert instead of create()/
     * insert() throughout.
     *
     * Returns the plaintext reset token (caller must send via email; never log).
     */
    private function seedTenantDefaults(array $data): string
    {
        Collection::firstOrCreate(
            ['slug' => 'default'],
            ['name' => 'Default', 'is_active' => true],
        );

        Setting::set('store_name', $data['name'] ?? 'My Store');
        Setting::set('currency', 'EUR');
        Setting::set('timezone', 'Europe/Rome');
        Setting::set('admin_email', $data['admin_email']);

        // Store admin user with a locked password so they must use the reset
        // link in the welcome email to gain access. firstOrCreate: a retry
        // must reuse the existing admin account, not fail on a duplicate email.
        User::firstOrCreate(
            ['email' => $data['admin_email']],
            ['name' => 'Store Admin', 'password' => Str::random(32)],
        );

        // Fresh password-reset token every call (email is the primary key here,
        // so a retry must overwrite the previous token, not fail on it — the
        // earlier token becomes invalid, which is correct: only the token in
        // the most recently (re)sent welcome email should work).
        $token = Str::random(64);
        DB::table('password_reset_tokens')->updateOrInsert(
            ['email' => $data['admin_email']],
            ['token' => Hash::make($token), 'created_at' => now()],
        );

        return $token;
    }
}
