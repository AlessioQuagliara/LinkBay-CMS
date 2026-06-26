<?php

namespace App\Filament\Tenant\Resources\StorePageResource\Pages;

use App\Filament\Tenant\Resources\StorePageResource;
use App\Services\LayoutBlockSchema;
use Filament\Actions\DeleteAction;
use Filament\Notifications\Notification;
use Filament\Resources\Pages\EditRecord;

class EditStorePage extends EditRecord
{
    protected static string $resource = StorePageResource::class;

    protected function getHeaderActions(): array
    {
        return [
            DeleteAction::make(),
        ];
    }

    protected function mutateFormDataBeforeSave(array $data): array
    {
        $agency = null;
        try {
            if (function_exists('tenancy') && tenancy()->initialized) {
                $agency = tenant()?->agency;
            }
        } catch (\Throwable) {
        }

        if ($agency) {
            $violation = LayoutBlockSchema::premiumViolation($data['content'] ?? [], $agency);

            if ($violation !== null) {
                Notification::make()->title('Blocco premium non autorizzato')->body($violation)->danger()->send();
                $this->halt();
            }
        }

        return $data;
    }
}
