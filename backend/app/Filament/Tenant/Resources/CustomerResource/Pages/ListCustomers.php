<?php
namespace App\Filament\Tenant\Resources\CustomerResource\Pages;
use App\Filament\Tenant\Resources\CustomerResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;
class ListCustomers extends ListRecords {
    protected static string $resource = CustomerResource::class;
    protected function getHeaderActions(): array { return [Actions\CreateAction::make()]; }

    public function getEmptyStateHeading(): string { return "Nessun cliente"; }
    public function getEmptyStateDescription(): string { return "I clienti registrati appariranno qui."; }
    public function getEmptyStateIcon(): string { return "heroicon-o-users"; }
}
