<?php

declare(strict_types=1);

namespace App\Filament\Admin\Resources\FailedJobResource\Pages;

use App\Filament\Admin\Resources\FailedJobResource;
use Filament\Resources\Pages\ListRecords;

class ListFailedJobs extends ListRecords
{
    protected static string $resource = FailedJobResource::class;

    protected function getHeaderActions(): array
    {
        return [];
    }
}
