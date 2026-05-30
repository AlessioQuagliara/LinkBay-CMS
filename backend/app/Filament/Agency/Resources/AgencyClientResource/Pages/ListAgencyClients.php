<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources\AgencyClientResource\Pages;

use App\Filament\Agency\Resources\AgencyClientResource;
use Filament\Resources\Pages\ListRecords;

class ListAgencyClients extends ListRecords
{
    protected static string $resource = AgencyClientResource::class;

    protected function getHeaderActions(): array
    {
        return [
            \Filament\Actions\CreateAction::make()->label('Nuovo cliente'),
        ];
    }
}
