<?php

declare(strict_types=1);

namespace App\Filament\Admin\Resources\AgencyEntitlementResource\Pages;

use App\Filament\Admin\Resources\AgencyEntitlementResource;
use App\Models\Central\AuditEvent;
use App\Services\AuditEventService;
use Filament\Resources\Pages\CreateRecord;

class CreateAgencyEntitlement extends CreateRecord
{
    protected static string $resource = AgencyEntitlementResource::class;

    protected function afterCreate(): void
    {
        app(AuditEventService::class)->log(
            event: AuditEvent::EVENT_ENTITLEMENT_GRANTED,
            agencyId: $this->record->agency_id,
            subjectType: 'agency_entitlement',
            subjectId: $this->record->id,
            newValues: [
                'catalog_item_id' => $this->record->catalog_item_id,
                'source' => $this->record->source,
                'status' => $this->record->status,
            ],
        );
    }
}
