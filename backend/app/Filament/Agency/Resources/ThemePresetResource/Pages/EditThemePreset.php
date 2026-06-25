<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources\ThemePresetResource\Pages;

use App\Filament\Agency\Resources\ThemePresetResource;
use App\Models\Central\AuditEvent;
use App\Models\Central\ThemePreset;
use App\Plugins\PluginRegistry;
use App\Services\AuditEventService;
use App\Services\ThemeConfigSchema;
use App\Services\ThemeForkResolver;
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
        // For forks: fill form with the RESOLVED config (parent base + existing overrides)
        // so inherited values are pre-populated and the agency sees the full effective config.
        $config = $this->record->isFork()
            ? $this->record->resolvedConfig()
            : ($data['config'] ?? []);

        return array_merge($data, ThemeConfigSchema::flattenForForm($config));
    }

    protected function mutateFormDataBeforeSave(array $data): array
    {
        $newConfig = ThemeConfigSchema::normalize(ThemeConfigSchema::packFromForm($data));

        if ($this->record->isFork()) {
            // Compute what the agency actually changed vs. the parent base config.
            // Only differences are persisted — no redundant storage of inherited values.
            $parentDef = app(PluginRegistry::class)->getTheme($this->record->parent_theme_slug);
            $baseConfig = ThemeConfigSchema::normalize($parentDef?->defaultConfig ?? []);

            $data['override_config'] = ThemeForkResolver::computeOverrides($baseConfig, $newConfig);
            // Update config snapshot = resolved (base + current overrides) for backward compat
            $data['config'] = ThemeForkResolver::applyOverrides($baseConfig, $data['override_config']);
        } else {
            $data['config'] = $newConfig;
        }

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
