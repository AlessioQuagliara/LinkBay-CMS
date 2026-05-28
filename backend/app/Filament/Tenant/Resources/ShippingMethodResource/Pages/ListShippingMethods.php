<?php
namespace App\Filament\Tenant\Resources\ShippingMethodResource\Pages;
use App\Filament\Tenant\Resources\ShippingMethodResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;
class ListShippingMethods extends ListRecords {
    protected static string $resource = ShippingMethodResource::class;
    protected function getHeaderActions(): array { return [Actions\CreateAction::make()]; }
}
