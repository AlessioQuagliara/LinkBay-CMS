<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources\ThemePresetResource\Pages;

use App\Filament\Agency\Resources\ThemePresetResource;
use App\Filament\Agency\Widgets\ThemePremiumNudgeWidget;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;

class ListThemePresets extends ListRecords
{
    protected static string $resource = ThemePresetResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\CreateAction::make()->label('Nuovo tema'),
        ];
    }

    protected function getHeaderWidgets(): array
    {
        return [
            ThemePremiumNudgeWidget::class,
        ];
    }
}
