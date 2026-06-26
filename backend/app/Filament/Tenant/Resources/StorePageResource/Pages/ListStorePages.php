<?php

namespace App\Filament\Tenant\Resources\StorePageResource\Pages;

use App\Filament\Tenant\Resources\StorePageResource;
use Filament\Actions\CreateAction;
use Filament\Resources\Pages\ListRecords;

class ListStorePages extends ListRecords
{
    protected static string $resource = StorePageResource::class;

    protected function getHeaderActions(): array
    {
        return [
            CreateAction::make(),
        ];
    }
}
