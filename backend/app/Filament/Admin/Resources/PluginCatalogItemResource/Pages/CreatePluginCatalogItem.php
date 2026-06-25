<?php

declare(strict_types=1);

namespace App\Filament\Admin\Resources\PluginCatalogItemResource\Pages;

use App\Filament\Admin\Resources\PluginCatalogItemResource;
use Filament\Resources\Pages\CreateRecord;

class CreatePluginCatalogItem extends CreateRecord
{
    protected static string $resource = PluginCatalogItemResource::class;
}
