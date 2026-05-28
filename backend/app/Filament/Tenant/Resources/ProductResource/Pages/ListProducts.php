<?php

namespace App\Filament\Tenant\Resources\ProductResource\Pages;

use App\Filament\Tenant\Resources\ProductResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;

class ListProducts extends ListRecords
{
    protected static string $resource = ProductResource::class;

    protected function getHeaderActions(): array
    {
        return [Actions\CreateAction::make()];
    }

    public function getEmptyStateHeading(): string { return "Nessun prodotto"; }
    public function getEmptyStateDescription(): string { return "Aggiungi il primo prodotto per iniziare a vendere."; }
    public function getEmptyStateIcon(): string { return "heroicon-o-shopping-bag"; }
}
