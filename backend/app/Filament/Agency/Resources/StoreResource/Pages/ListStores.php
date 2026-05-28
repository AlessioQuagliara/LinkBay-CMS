<?php
namespace App\Filament\Agency\Resources\StoreResource\Pages;
use App\Filament\Agency\Resources\StoreResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;
class ListStores extends ListRecords {
    protected static string $resource = StoreResource::class;
    protected function getHeaderActions(): array { return [Actions\CreateAction::make()]; }
}
