<?php

declare(strict_types=1);

namespace App\Models\Central;

use Stancl\Tenancy\Contracts\TenantWithDatabase;
use Stancl\Tenancy\Database\Concerns\HasDatabase;
use Stancl\Tenancy\Database\Concerns\HasDomains;
use Stancl\Tenancy\Database\Models\Tenant as BaseTenant;

class Tenant extends BaseTenant implements TenantWithDatabase
{
    use HasDatabase, HasDomains;

    protected $connection = 'central';

    /**
     * Override stancl's CentralConnection trait which reads DB_CONNECTION env var.
     * We always want the 'central' named connection regardless of the default.
     */
    public function getConnectionName(): string
    {
        return 'central';
    }

    public static function getCustomColumns(): array
    {
        return [
            'id',
            'name',
            'plan_id',
            'agency_id',
            'agency_client_id',
            'status',
        ];
    }

    public function plan()
    {
        return $this->belongsTo(Plan::class);
    }

    public function subscription()
    {
        return $this->hasOne(Subscription::class);
    }

    public function agency()
    {
        return $this->belongsTo(Agency::class);
    }

    public function agencyClient()
    {
        return $this->belongsTo(AgencyClient::class);
    }

    public function brandName(): string
    {
        return $this->agency?->brand_name ?? $this->name;
    }

    public function brandLogo(): ?string
    {
        return $this->agency?->logo_url;
    }
}
