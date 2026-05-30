<?php

namespace App\Filament\Admin\Resources\JobApplicationResource\Pages;

use App\Filament\Admin\Resources\JobApplicationResource;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;

class ViewJobApplication extends EditRecord
{
    protected static string $resource = JobApplicationResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\Action::make('download_cv')
                ->label('Download CV')
                ->icon('heroicon-o-document-arrow-down')
                ->url(fn () => route('admin.careers.cv.download', $this->record))
                ->openUrlInNewTab(),
            Actions\DeleteAction::make(),
        ];
    }

    protected function mutateFormDataBeforeFill(array $data): array
    {
        if ($data['status'] === 'new') {
            $this->record->update(['status' => 'reviewing']);
            $data['status'] = 'reviewing';
        }
        return $data;
    }

    protected function getSavedNotificationTitle(): ?string
    {
        return 'Application updated';
    }
}
