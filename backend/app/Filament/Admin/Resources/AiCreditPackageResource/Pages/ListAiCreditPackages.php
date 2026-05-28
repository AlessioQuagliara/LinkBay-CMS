<?php
namespace App\Filament\Admin\Resources\AiCreditPackageResource\Pages;
use App\Filament\Admin\Resources\AiCreditPackageResource;
use Filament\Actions;
use Filament\Resources\Pages\ListRecords;
class ListAiCreditPackages extends ListRecords {
    protected static string $resource = AiCreditPackageResource::class;
    protected function getHeaderActions(): array { return [Actions\CreateAction::make()]; }
}
