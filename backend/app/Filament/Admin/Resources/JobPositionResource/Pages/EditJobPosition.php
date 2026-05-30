<?php

namespace App\Filament\Admin\Resources\JobPositionResource\Pages;

use App\Filament\Admin\Resources\JobPositionResource;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;

class EditJobPosition extends EditRecord
{
    protected static string $resource = JobPositionResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\DeleteAction::make(),
        ];
    }

    protected function getSavedNotificationTitle(): ?string
    {
        return 'Position saved';
    }
}
