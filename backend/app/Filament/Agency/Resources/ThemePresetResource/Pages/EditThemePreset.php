<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources\ThemePresetResource\Pages;

use App\Filament\Agency\Resources\ThemePresetResource;
use App\Models\Central\AuditEvent;
use App\Models\Central\ThemePreset;
use App\Services\AuditEventService;
use App\Services\ThemeConfigSchema;
use Filament\Actions\Action;
use Filament\Actions\DeleteAction;
use Filament\Notifications\Notification;
use Filament\Resources\Pages\EditRecord;

class EditThemePreset extends EditRecord
{
    protected static string $resource = ThemePresetResource::class;

    protected array $auditOldValues = [];

    public function mount(int|string $record): void
    {
        parent::mount($record);

        // System presets are read-only — redirect to index.
        if ($this->record->is_system) {
            Notification::make()->title('I preset di sistema non sono modificabili.')->warning()->send();
            $this->redirect($this->getResource()::getUrl('index'));
        }
    }

    protected function mutateFormDataBeforeFill(array $data): array
    {
        // Unpack nested config into flat form fields for the color pickers / selects.
        return array_merge($data, ThemeConfigSchema::flattenForForm($data['config'] ?? []));
    }

    protected function mutateFormDataBeforeSave(array $data): array
    {
        // Pack flat form fields into a normalized config, then strip the flat fields.
        $data['config'] = ThemeConfigSchema::normalize(ThemeConfigSchema::packFromForm($data));
        foreach (ThemeConfigSchema::formFieldNames() as $field) {
            unset($data[$field]);
        }

        return $data;
    }

    protected function getHeaderActions(): array
    {
        return [
            Action::make('activate')
                ->label('Attiva')
                ->icon('heroicon-o-check-circle')
                ->color('success')
                ->visible(fn () => $this->record->isDraft())
                ->requiresConfirmation()
                ->action(function (): void {
                    $this->record->activate();

                    app(AuditEventService::class)->log(
                        event: AuditEvent::EVENT_THEME_ACTIVATED,
                        subjectType: 'theme_preset',
                        subjectId: (string) $this->record->id,
                        newValues: ['status' => ThemePreset::STATUS_ACTIVE],
                    );

                    Notification::make()->title('Tema attivato')->success()->send();
                    $this->refreshFormData(['status']);
                }),

            Action::make('deactivate')
                ->label('Disattiva')
                ->icon('heroicon-o-x-circle')
                ->color('warning')
                ->visible(fn () => $this->record->isActive())
                ->requiresConfirmation()
                ->action(function (): void {
                    $this->record->deactivate();

                    app(AuditEventService::class)->log(
                        event: AuditEvent::EVENT_THEME_ACTIVATED,
                        subjectType: 'theme_preset',
                        subjectId: (string) $this->record->id,
                        newValues: ['status' => ThemePreset::STATUS_DRAFT],
                    );

                    Notification::make()->title('Tema disattivato')->warning()->send();
                    $this->refreshFormData(['status']);
                }),

            DeleteAction::make(),
        ];
    }

    protected function beforeSave(): void
    {
        $this->auditOldValues = $this->record->only(['name', 'slug', 'status']);
    }

    protected function afterSave(): void
    {
        $newValues = $this->record->only(['name', 'slug', 'status']);
        $changed = array_diff_assoc($newValues, $this->auditOldValues);

        if (empty($changed)) {
            return;
        }

        app(AuditEventService::class)->log(
            event: AuditEvent::EVENT_THEME_UPDATED,
            subjectType: 'theme_preset',
            subjectId: (string) $this->record->id,
            oldValues: array_intersect_key($this->auditOldValues, $changed),
            newValues: $changed,
        );
    }
}
