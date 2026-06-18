<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources\LayoutTemplateResource\Pages;

use App\Filament\Agency\Resources\LayoutTemplateResource;
use App\Models\Central\AuditEvent;
use App\Services\AuditEventService;
use Filament\Resources\Pages\CreateRecord;

class CreateLayoutTemplate extends CreateRecord
{
    protected static string $resource = LayoutTemplateResource::class;

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
            event: AuditEvent::EVENT_LAYOUT_CREATED,
            subjectType: 'layout_template',
            subjectId: (string) $this->record->id,
            newValues: [
                'name' => $this->record->name,
                'slug' => $this->record->slug,
                'status' => $this->record->status,
            ],
        );
    }

    protected function getRedirectUrl(): string
    {
        return $this->getResource()::getUrl('edit', ['record' => $this->record]);
    }
}
