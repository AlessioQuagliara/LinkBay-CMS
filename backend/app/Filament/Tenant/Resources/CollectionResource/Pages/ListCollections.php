<?php
namespace App\Filament\Tenant\Resources\CollectionResource\Pages;
use App\Filament\Tenant\Resources\CollectionResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;
class ListCollections extends ListRecords {
    protected static string $resource = CollectionResource::class;
    protected function getHeaderActions(): array { return [Actions\CreateAction::make()]; }
}
