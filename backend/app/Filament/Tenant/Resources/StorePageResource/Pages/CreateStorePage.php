<?php

namespace App\Filament\Tenant\Resources\StorePageResource\Pages;

use App\Filament\Tenant\Resources\StorePageResource;
use App\Services\LayoutBlockSchema;
use Filament\Notifications\Notification;
use Filament\Resources\Pages\CreateRecord;

class CreateStorePage extends CreateRecord
{
    protected static string $resource = StorePageResource::class;

    protected function mutateFormDataBeforeCreate(array $data): array
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

    protected function getRedirectUrl(): string
    {
        return $this->getResource()::getUrl('edit', ['record' => $this->record]);
    }
}
