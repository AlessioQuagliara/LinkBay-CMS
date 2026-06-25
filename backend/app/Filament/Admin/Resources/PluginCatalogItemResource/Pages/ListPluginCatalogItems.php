<?php

declare(strict_types=1);

namespace App\Filament\Admin\Resources\PluginCatalogItemResource\Pages;

use App\Filament\Admin\Resources\PluginCatalogItemResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;

class ListPluginCatalogItems extends ListRecords
{
    protected static string $resource = PluginCatalogItemResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\CreateAction::make(),
        ];
    }
}
