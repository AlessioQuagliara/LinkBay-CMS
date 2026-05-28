<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Central\Tenant;
use Illuminate\Support\Facades\Hash;

class TenantProvisioningService
{
    public function provision(array $data): Tenant
    {
        $tenant = Tenant::create([
            'id' => $data['domain'],
            'name' => $data['name'],
            'plan_id' => $data['plan_id'] ?? null,
            'status' => 'active',
        ]);

        $tenant->domains()->create(['domain' => $data['domain']]);

        tenancy()->initialize($tenant);

        $this->seedTenantDefaults($data);

        tenancy()->end();

        return $tenant;
    }

    public function deprovision(Tenant $tenant): void
    {
        $tenant->delete();
    }

    private function seedTenantDefaults(array $data): void
    {
        \App\Models\Tenant\Collection::create([
            'name' => 'Default',
            'slug' => 'default',
            'is_active' => true,
        ]);

        \App\Models\Tenant\Setting::set('store_name', $data['name'] ?? 'My Store');
        \App\Models\Tenant\Setting::set('currency', 'EUR');
        \App\Models\Tenant\Setting::set('timezone', 'Europe/Rome');
        \App\Models\Tenant\Setting::set('admin_email', $data['admin_email']);
    }
}
