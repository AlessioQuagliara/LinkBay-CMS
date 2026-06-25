<?php

declare(strict_types=1);

namespace App\Filament\Admin\Resources\PluginCatalogItemResource\Pages;

use App\Filament\Admin\Resources\PluginCatalogItemResource;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;

class EditPluginCatalogItem extends EditRecord
{
    protected static string $resource = PluginCatalogItemResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\DeleteAction::make(),
        ];
    }
}
