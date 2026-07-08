<?php

declare(strict_types=1);

namespace App\Filament\Admin\Resources\BillingEventResource\Pages;

use App\Filament\Admin\Resources\BillingEventResource;
use Filament\Resources\Pages\ListRecords;

class ListBillingEvents extends ListRecords
{
    protected static string $resource = BillingEventResource::class;

    protected function getHeaderActions(): array
    {
        return [];
    }
}
