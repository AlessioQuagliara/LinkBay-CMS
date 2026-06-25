<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources\LayoutTemplateResource\Pages;

use App\Filament\Agency\Resources\LayoutTemplateResource;
use App\Models\Central\AuditEvent;
use App\Models\Central\LayoutTemplate;
use App\Models\Central\UsageEvent;
use App\Services\AuditEventService;
use App\Services\LayoutBlockSchema;
use App\Services\UsageEventService;
use Filament\Actions\Action;
use Filament\Actions\DeleteAction;
use Filament\Notifications\Notification;
use Filament\Resources\Pages\EditRecord;

class EditLayoutTemplate extends EditRecord
{
    protected static string $resource = LayoutTemplateResource::class;

    protected array $auditOldValues = [];

    protected function getHeaderActions(): array
    {
        return [
            Action::make('publish')
                ->label('Pubblica')
                ->icon('heroicon-o-eye')
                ->color('success')
                ->visible(fn () => $this->record->isDraft())
                ->requiresConfirmation()
                ->action(function (): void {
                    $this->record->publish();

                    app(AuditEventService::class)->log(
                        event: AuditEvent::EVENT_LAYOUT_PUBLISHED,
                        subjectType: 'layout_template',
                        subjectId: (string) $this->record->id,
                        newValues: ['status' => LayoutTemplate::STATUS_PUBLISHED],
                    );

                    Notification::make()->title('Template pubblicato')->success()->send();
                    $this->refreshFormData(['status']);
                }),

            Action::make('unpublish')
                ->label('Torna in bozza')
                ->icon('heroicon-o-eye-slash')
                ->color('warning')
                ->visible(fn () => $this->record->isPublished())
                ->requiresConfirmation()
                ->action(function (): void {
                    $this->record->unpublish();

                    app(AuditEventService::class)->log(
                        event: AuditEvent::EVENT_LAYOUT_PUBLISHED,
                        subjectType: 'layout_template',
                        subjectId: (string) $this->record->id,
                        newValues: ['status' => LayoutTemplate::STATUS_DRAFT],
                    );

                    Notification::make()->title('Template rimesso in bozza')->warning()->send();
                    $this->refreshFormData(['status']);
                }),

            DeleteAction::make(),
        ];
    }

    protected function beforeSave(): void
    {
        $this->auditOldValues = $this->record->only(['name', 'slug', 'status']);

        $agency = app()->has('current_agency') ? app('current_agency') : null;

        if ($agency) {
            $blocks = $this->data['blocks'] ?? [];
            $violation = LayoutBlockSchema::premiumViolation($blocks, $agency);

            if ($violation !== null) {
                Notification::make()->title('Blocco premium non autorizzato')->body($violation)->danger()->send();
                $this->halt();
            }
        }
    }

    protected function afterSave(): void
    {
        app(UsageEventService::class)->track(
            eventType: UsageEvent::EVENT_LAYOUT_SAVED,
            subjectType: 'layout_template',
            subjectId: $this->record->id,
        );

        $newValues = $this->record->only(['name', 'slug', 'status']);
        $changed = array_diff_assoc($newValues, $this->auditOldValues);

        if (empty($changed)) {
            return;
        }

        app(AuditEventService::class)->log(
            event: AuditEvent::EVENT_LAYOUT_UPDATED,
            subjectType: 'layout_template',
            subjectId: (string) $this->record->id,
            oldValues: array_intersect_key($this->auditOldValues, $changed),
            newValues: $changed,
        );
    }
}
