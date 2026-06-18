<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Central\Tenant;
use App\Models\Tenant\Collection;
use App\Models\Tenant\Setting;
use App\Models\Tenant\User;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Hash;
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

    public function deprovision(Tenant $tenant): void
    {
        $tenant->delete();
    }

    /**
     * Seeds initial data into the tenant database while tenancy is active.
     * Creates the admin user and generates a password-reset token.
     *
     * Returns the plaintext reset token (caller must send via email; never log).
     */
    private function seedTenantDefaults(array $data): string
    {
        Collection::create([
            'name' => 'Default',
            'slug' => 'default',
            'is_active' => true,
        ]);

        Setting::set('store_name', $data['name'] ?? 'My Store');
        Setting::set('currency', 'EUR');
        Setting::set('timezone', 'Europe/Rome');
        Setting::set('admin_email', $data['admin_email']);

        // Create the store admin user with a locked password so they must
        // use the reset link in the welcome email to gain access.
        User::create([
            'name' => 'Store Admin',
            'email' => $data['admin_email'],
            'password' => Str::random(32),
        ]);

        // Generate a password-reset token and store it in the tenant DB.
        $token = Str::random(64);
        DB::table('password_reset_tokens')->insert([
            'email' => $data['admin_email'],
            'token' => Hash::make($token),
            'created_at' => now(),
        ]);

        return $token;
    }
}
