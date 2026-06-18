<?php

declare(strict_types=1);

namespace App\Jobs;

use App\Mail\StoreAdminWelcomeMail;
use App\Models\Central\Tenant;
use App\Services\TenantProvisioningService;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Mail;

/**
 * Initialises the tenant database schema and seeds defaults.
 *
 * Dispatched asynchronously after store creation so that tenancy()->initialize()
 * never runs inside a Livewire request (which would corrupt the DB connection).
 */
class ProvisionTenantDatabaseJob implements ShouldQueue
{
    use Queueable;

    public int $tries = 3;

    public function __construct(
        public readonly string $tenantId,
        public readonly ?string $adminEmail = null,
    ) {}

    public function handle(TenantProvisioningService $service): void
    {
        $tenant = Tenant::find($this->tenantId);

        if (! $tenant) {
            Log::warning('ProvisionTenantDatabaseJob: tenant not found', ['id' => $this->tenantId]);

            return;
        }

        $resetToken = $service->initializeDatabase($tenant, $this->adminEmail);

        if ($this->adminEmail !== null && $resetToken !== null) {
            $this->sendWelcomeEmail($tenant, $this->adminEmail, $resetToken);
        }
    }

    private function sendWelcomeEmail(Tenant $tenant, string $adminEmail, string $resetToken): void
    {
        $storeDomain = config('app.store_domain', 'yoursite-linkbay-cms.com');
        $storeBaseUrl = 'https://'.$tenant->id.'.'.$storeDomain;
        $storeUrl = $storeBaseUrl.'/admin';
        $resetUrl = $storeBaseUrl.'/admin/password-reset/reset'
            .'?token='.urlencode($resetToken)
            .'&email='.urlencode($adminEmail);

        Mail::to($adminEmail)->send(new StoreAdminWelcomeMail(
            storeName: $tenant->name,
            storeUrl: $storeUrl,
            resetUrl: $resetUrl,
        ));
    }
}
