<?php
namespace App\Filament\Agency\Resources\StoreResource\Pages;
use App\Filament\Agency\Resources\StoreResource;
use Filament\Actions;
use Filament\Resources\Pages\EditRecord;
class EditStore extends EditRecord {
    protected static string $resource = StoreResource::class;
    protected function getHeaderActions(): array { return [Actions\DeleteAction::make()]; }
}
