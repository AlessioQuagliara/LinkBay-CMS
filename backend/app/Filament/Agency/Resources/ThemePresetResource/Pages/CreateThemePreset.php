<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources\ThemePresetResource\Pages;

use App\Filament\Agency\Resources\ThemePresetResource;
use App\Models\Central\AuditEvent;
use App\Services\AuditEventService;
use App\Services\ThemeConfigSchema;
use Filament\Resources\Pages\CreateRecord;

class CreateThemePreset extends CreateRecord
{
    protected static string $resource = ThemePresetResource::class;

    protected function mutateFormDataBeforeCreate(array $data): array
    {
        $agency = app()->has('current_agency') ? app('current_agency') : null;

        if (! $agency) {
            $this->halt();
        }

        $data['agency_id'] = $agency->id;
        $data['is_system'] = false;

        // Pack flat form fields into normalized config, then strip them.
        $data['config'] = ThemeConfigSchema::normalize(ThemeConfigSchema::packFromForm($data));
        foreach (ThemeConfigSchema::formFieldNames() as $field) {
            unset($data[$field]);
        }

        return $data;
    }

    protected function afterCreate(): void
    {
        app(AuditEventService::class)->log(
            event: AuditEvent::EVENT_THEME_CREATED,
            subjectType: 'theme_preset',
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
