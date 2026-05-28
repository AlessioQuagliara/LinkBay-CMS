<?php
namespace App\Filament\Tenant\Resources\DiscountCodeResource\Pages;
use App\Filament\Tenant\Resources\DiscountCodeResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;
class ListDiscountCodes extends ListRecords {
    protected static string $resource = DiscountCodeResource::class;
    protected function getHeaderActions(): array { return [Actions\CreateAction::make()]; }

    public function getEmptyStateHeading(): string { return "Nessun codice sconto"; }
    public function getEmptyStateDescription(): string { return "Crea il primo codice per le tue promozioni."; }
    public function getEmptyStateIcon(): string { return "heroicon-o-tag"; }
}
