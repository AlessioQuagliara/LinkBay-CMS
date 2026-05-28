<?php
namespace App\Filament\Tenant\Resources\ShippingMethodResource\Pages;
use App\Filament\Tenant\Resources\ShippingMethodResource;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;
class EditShippingMethods extends EditRecord {
    protected static string $resource = ShippingMethodResource::class;
    protected function getHeaderActions(): array { return [Actions\DeleteAction::make()]; }
}
