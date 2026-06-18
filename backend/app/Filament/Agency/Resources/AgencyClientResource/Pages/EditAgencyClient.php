<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources\AgencyClientResource\Pages;

use App\Filament\Agency\Resources\AgencyClientResource;
use App\Models\Central\AuditEvent;
use App\Services\AuditEventService;
use Filament\Actions\DeleteAction;
use Filament\Resources\Pages\EditRecord;

class EditAgencyClient extends EditRecord
{
    protected static string $resource = AgencyClientResource::class;

    /** @var array<string, mixed> */
    protected array $auditOldValues = [];

    protected function getHeaderActions(): array
    {
        return [
            DeleteAction::make(),
        ];
    }

    protected function beforeSave(): void
    {
        $watched = ['name', 'legal_name', 'billing_email', 'status', 'country', 'vat_number'];

        $this->auditOldValues = array_intersect_key(
            $this->record->getOriginal(),
            array_flip($watched),
        );
    }

    protected function afterSave(): void
    {
        $watched = ['name', 'legal_name', 'billing_email', 'status', 'country', 'vat_number'];

        $newValues = $this->record->only($watched);
        $changed = array_diff_assoc($newValues, $this->auditOldValues);

        if (empty($changed)) {
            return;
        }

        app(AuditEventService::class)->log(
            event: AuditEvent::EVENT_CLIENT_UPDATED,
            subjectType: 'agency_client',
            subjectId: (string) $this->record->id,
            oldValues: array_intersect_key($this->auditOldValues, $changed),
            newValues: $changed,
        );
    }
}
