<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Central\Tenant;

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
            'id'               => $data['domain'],
            'name'             => $data['name'],
            'plan_id'          => $data['plan_id'] ?? null,
            'agency_id'        => $data['agency_id'] ?? null,
            'agency_client_id' => $data['agency_client_id'] ?? null,
            'status'           => 'active',
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
        $fullDomain  = $tenant->id . '.' . $storeDomain;

        if (! $tenant->domains()->where('domain', $fullDomain)->exists()) {
            $tenant->domains()->create(['domain' => $fullDomain]);
        }
    }

    /**
     * Initializes the tenant database schema and seeds defaults.
     * Can be called independently for re-provisioning or recovery.
     */
    public function initializeDatabase(Tenant $tenant, ?string $adminEmail = null): void
    {
        $email = $adminEmail
            ?? (isset($tenant->admin_email) ? $tenant->admin_email : null)
            ?? 'admin@' . $tenant->id . '.test';

        tenancy()->initialize($tenant);
        try {
            $this->seedTenantDefaults([
                'name'        => $tenant->name,
                'admin_email' => $email,
            ]);
        } finally {
            // Always restore central connection, even if seeding throws.
            tenancy()->end();
        }
    }

    public function deprovision(Tenant $tenant): void
    {
        $tenant->delete();
    }

    private function seedTenantDefaults(array $data): void
    {
        \App\Models\Tenant\Collection::create([
            'name'      => 'Default',
            'slug'      => 'default',
            'is_active' => true,
        ]);

        \App\Models\Tenant\Setting::set('store_name', $data['name'] ?? 'My Store');
        \App\Models\Tenant\Setting::set('currency', 'EUR');
        \App\Models\Tenant\Setting::set('timezone', 'Europe/Rome');
        \App\Models\Tenant\Setting::set('admin_email', $data['admin_email']);
    }
}
