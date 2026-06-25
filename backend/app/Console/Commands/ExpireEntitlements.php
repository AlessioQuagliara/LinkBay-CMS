<?php

declare(strict_types=1);

namespace App\Console\Commands;

use App\Models\Central\AgencyEntitlement;
use App\Models\Central\AuditEvent;
use App\Services\AuditEventService;
use Illuminate\Console\Command;

class ExpireEntitlements extends Command
{
    protected $signature = 'entitlements:expire';

    protected $description = 'Marca come expired gli entitlements attivi con ends_at scaduto';

    public function handle(AuditEventService $audit): int
    {
        $expired = AgencyEntitlement::query()
            ->where('status', AgencyEntitlement::STATUS_ACTIVE)
            ->whereNotNull('ends_at')
            ->where('ends_at', '<', now())
            ->with('catalogItem')
            ->get();

        if ($expired->isEmpty()) {
            $this->info('Nessun entitlement da scadere.');

            return self::SUCCESS;
        }

        foreach ($expired as $entitlement) {
            $entitlement->expire();

            $audit->log(
                event: AuditEvent::EVENT_ENTITLEMENT_EXPIRED,
                agencyId: $entitlement->agency_id,
                subjectType: 'agency_entitlement',
                subjectId: $entitlement->id,
                newValues: [
                    'status' => AgencyEntitlement::STATUS_EXPIRED,
                    'code' => $entitlement->catalogItem?->code,
                ],
            );
        }

        $this->info("Scaduti {$expired->count()} entitlement(s).");

        return self::SUCCESS;
    }
}
