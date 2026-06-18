<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources\AgencyClientResource\Pages;

use App\Filament\Agency\Resources\AgencyClientResource;
use App\Models\Central\AuditEvent;
use App\Services\AuditEventService;
use Filament\Resources\Pages\CreateRecord;

class CreateAgencyClient extends CreateRecord
{
    protected static string $resource = AgencyClientResource::class;

    protected function mutateFormDataBeforeCreate(array $data): array
    {
        $agency = app()->has('current_agency') ? app('current_agency') : null;

        if (! $agency) {
            $this->halt();
        }

        $data['agency_id'] = $agency->id;

        return $data;
    }

    protected function afterCreate(): void
    {
        app(AuditEventService::class)->log(
            event: AuditEvent::EVENT_CLIENT_CREATED,
            subjectType: 'agency_client',
            subjectId: (string) $this->record->id,
            newValues: [
                'name' => $this->record->name,
                'billing_email' => $this->record->billing_email,
                'status' => $this->record->status,
            ],
        );
    }

    protected function getRedirectUrl(): string
    {
        return $this->getResource()::getUrl('edit', ['record' => $this->record]);
    }
}
