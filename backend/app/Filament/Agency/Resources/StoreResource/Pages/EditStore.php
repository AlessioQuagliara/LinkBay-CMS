<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources\StoreResource\Pages;

use App\Filament\Agency\Resources\StoreResource;
use App\Models\Central\AuditEvent;
use App\Services\AuditEventService;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;

class EditStore extends EditRecord
{
    protected static string $resource = StoreResource::class;

    /** @var array<string, mixed> */
    protected array $auditOldValues = [];

    protected function getHeaderActions(): array
    {
        return [Actions\DeleteAction::make()];
    }

    protected function beforeSave(): void
    {
        $watched = ['name', 'status', 'agency_client_id'];

        $this->auditOldValues = array_intersect_key(
            $this->record->getOriginal(),
            array_flip($watched),
        );
    }

    protected function afterSave(): void
    {
        $watched = ['name', 'status', 'agency_client_id'];

        $newValues = $this->record->only($watched);
        $changed = array_diff_assoc($newValues, $this->auditOldValues);

        if (empty($changed)) {
            return;
        }

        app(AuditEventService::class)->log(
            event: AuditEvent::EVENT_STORE_UPDATED,
            subjectType: 'store',
            subjectId: $this->record->id,
            oldValues: array_intersect_key($this->auditOldValues, $changed),
            newValues: $changed,
        );
    }
}
