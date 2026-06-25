<?php

declare(strict_types=1);

namespace App\Filament\Admin\Resources\AgencyHealthAlertResource\Pages;

use App\Filament\Admin\Resources\AgencyHealthAlertResource;
use Filament\Resources\Pages\ListRecords;

class ListAgencyHealthAlerts extends ListRecords
{
    protected static string $resource = AgencyHealthAlertResource::class;

    protected function getHeaderActions(): array
    {
        return [];
    }
}
