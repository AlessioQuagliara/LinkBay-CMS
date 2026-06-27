<?php

namespace App\Filament\Tenant\Resources\CategoryResource\Pages;

use App\Filament\Tenant\Resources\CategoryResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;

class ListCategories extends ListRecords
{
    protected static string $resource = CategoryResource::class;

    protected function getHeaderActions(): array
    {
        return [Actions\CreateAction::make()];
    }

    public function getEmptyStateHeading(): string
    {
        return 'Nessuna categoria';
    }

    public function getEmptyStateDescription(): string
    {
        return 'Crea la prima categoria per organizzare i tuoi prodotti.';
    }

    public function getEmptyStateIcon(): string
    {
        return 'heroicon-o-tag';
    }
}
