<?php
namespace App\Filament\Tenant\Resources\ShippingMethodResource\Pages;
use App\Filament\Tenant\Resources\ShippingMethodResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;
class ListShippingMethods extends ListRecords {
    protected static string $resource = ShippingMethodResource::class;
    protected function getHeaderActions(): array { return [Actions\CreateAction::make()]; }

    public function getEmptyStateHeading(): string { return "Nessun metodo di spedizione"; }
    public function getEmptyStateDescription(): string { return "Aggiungi almeno un metodo per gestire le consegne."; }
    public function getEmptyStateIcon(): string { return "heroicon-o-truck"; }
}
