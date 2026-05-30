<?php

namespace App\Filament\Admin\Resources\JobPositionResource\Pages;

use App\Filament\Admin\Resources\JobPositionResource;
use Filament\Resources\Pages\CreateRecord;

class CreateJobPosition extends CreateRecord
{
    protected static string $resource = JobPositionResource::class;

    protected function getRedirectUrl(): string
    {
        return $this->getResource()::getUrl('index');
    }
}
