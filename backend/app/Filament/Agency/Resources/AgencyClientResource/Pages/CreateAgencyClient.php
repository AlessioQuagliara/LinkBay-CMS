<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources\AgencyClientResource\Pages;

use App\Filament\Agency\Resources\AgencyClientResource;
use Filament\Resources\Pages\CreateRecord;

class CreateAgencyClient extends CreateRecord
{
    protected static string $resource = AgencyClientResource::class;

    protected function mutateFormDataBeforeCreate(array $data): array
    {
        $agency = app()->has('current_agency') ? app('current_agency') : null;

        if (!$agency) {
            $this->halt();
        }

        $data['agency_id'] = $agency->id;

        return $data;
    }

    protected function getRedirectUrl(): string
    {
        return $this->getResource()::getUrl('edit', ['record' => $this->record]);
    }
}
