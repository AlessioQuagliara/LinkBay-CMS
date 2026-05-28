<?php
namespace App\Filament\Tenant\Resources\DiscountCodeResource\Pages;
use App\Filament\Tenant\Resources\DiscountCodeResource;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;
class EditDiscountCodes extends EditRecord {
    protected static string $resource = DiscountCodeResource::class;
    protected function getHeaderActions(): array { return [Actions\DeleteAction::make()]; }
}
