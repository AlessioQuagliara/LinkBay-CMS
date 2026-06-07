<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources\AgencyMemberResource\Pages;

use App\Filament\Agency\Resources\AgencyMemberResource;
use Filament\Resources\Pages\ListRecords;

class ListAgencyMembers extends ListRecords
{
    protected static string $resource = AgencyMemberResource::class;
}
