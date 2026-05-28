<?php
namespace App\Filament\Tenant\Resources\CollectionResource\Pages;
use App\Filament\Tenant\Resources\CollectionResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;
class ListCollections extends ListRecords {
    protected static string $resource = CollectionResource::class;
    protected function getHeaderActions(): array { return [Actions\CreateAction::make()]; }

    public function getEmptyStateHeading(): string { return "Nessuna collezione"; }
    public function getEmptyStateDescription(): string { return "Crea la prima collezione per organizzare i prodotti."; }
    public function getEmptyStateIcon(): string { return "heroicon-o-folder"; }
}
