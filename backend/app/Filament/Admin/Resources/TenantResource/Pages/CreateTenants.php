<?php
namespace App\Filament\Admin\Resources\TenantResource\Pages;
use App\Filament\Admin\Resources\TenantResource;
use Filament\Actions;
use Filament\Resources\Pages\CreateRecord;
class CreateTenants extends CreateRecord {
    protected static string $resource = TenantResource::class;
    
}
