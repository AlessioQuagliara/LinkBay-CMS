<?php

declare(strict_types=1);

namespace App\Filament\Admin\Resources\AgencyEntitlementResource\Pages;

use App\Filament\Admin\Resources\AgencyEntitlementResource;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;

class EditAgencyEntitlement extends EditRecord
{
    protected static string $resource = AgencyEntitlementResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\DeleteAction::make(),
        ];
    }
}
