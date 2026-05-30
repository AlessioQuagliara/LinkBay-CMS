<?php

namespace App\Filament\Admin\Resources\JobPositionResource\Pages;

use App\Filament\Admin\Resources\JobPositionResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;

class ListJobPositions extends ListRecords
{
    protected static string $resource = JobPositionResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\CreateAction::make()->label('New position'),
        ];
    }
}
