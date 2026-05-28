<?php
namespace App\Filament\Tenant\Resources\OrderResource\Pages;
use App\Filament\Tenant\Resources\OrderResource;
use Filament\Resources\Pages\ListRecords;
class ListOrders extends ListRecords { protected static string $resource = OrderResource::class; 
    public function getEmptyStateHeading(): string { return "Nessun ordine"; }
    public function getEmptyStateDescription(): string { return "Gli ordini ricevuti appariranno qui."; }
    public function getEmptyStateIcon(): string { return "heroicon-o-shopping-cart"; }
}
