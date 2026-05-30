<?php

namespace App\Filament\Admin\Resources\ContactSubmissionResource\Pages;

use App\Filament\Admin\Resources\ContactSubmissionResource;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;

class ViewContactSubmission extends EditRecord
{
    protected static string $resource = ContactSubmissionResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\DeleteAction::make(),
        ];
    }

    protected function mutateFormDataBeforeFill(array $data): array
    {
        if ($data['status'] === 'new') {
            $this->record->update(['status' => 'read']);
            $data['status'] = 'read';
        }

        return $data;
    }

    protected function getSavedNotificationTitle(): ?string
    {
        return 'Status updated';
    }
}
