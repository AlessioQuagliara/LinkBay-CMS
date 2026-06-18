<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources\LayoutTemplateResource\Pages;

use App\Filament\Agency\Resources\LayoutTemplateResource;
use Filament\Actions\CreateAction;
use Filament\Resources\Pages\ListRecords;

class ListLayoutTemplates extends ListRecords
{
    protected static string $resource = LayoutTemplateResource::class;

    protected function getHeaderActions(): array
    {
        return [
            CreateAction::make()->label('Nuovo template'),
        ];
    }
}
