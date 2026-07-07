<?php

declare(strict_types=1);

namespace App\Filament\Tenant\Resources\ProductResource\Pages;

use App\Exports\Tenant\ProductExport;
use App\Filament\Tenant\Resources\ProductResource;
use App\Jobs\Tenant\ImportProductsJob;
use Filament\Actions;
use Filament\Forms;
use Filament\Notifications\Notification;
use Filament\Resources\Pages\ListRecords;
use Symfony\Component\HttpFoundation\StreamedResponse;

class ListProducts extends ListRecords
{
    protected static string $resource = ProductResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\CreateAction::make(),

            Actions\Action::make('import_csv')
                ->label('Importa CSV')
                ->icon('heroicon-o-arrow-up-tray')
                ->color('gray')
                ->form([
                    Forms\Components\FileUpload::make('csv_file')
                        ->label('File CSV')
                        ->acceptedFileTypes(['text/csv', 'application/csv', 'text/plain'])
                        ->maxSize(10240) // 10 MB
                        ->required()
                        ->helperText('Max 10 MB. Colonne richieste: name, price, sku. Vedi template.'),
                ])
                ->action(function (array $data): void {
                    $path = $data['csv_file'];

                    ImportProductsJob::dispatch(
                        $path,
                        auth()->id(),
                    );

                    Notification::make()
                        ->title('Importazione avviata')
                        ->body('Riceverai una notifica al termine del processo.')
                        ->success()
                        ->send();
                }),

            Actions\Action::make('download_template')
                ->label('Template CSV')
                ->icon('heroicon-o-arrow-down-tray')
                ->color('gray')
                ->action(fn (): StreamedResponse => app(ProductExport::class)->template()),

            Actions\Action::make('export_csv')
                ->label('Esporta CSV')
                ->icon('heroicon-o-table-cells')
                ->color('gray')
                ->action(fn (): StreamedResponse => app(ProductExport::class)->download()),
        ];
    }

    public function getEmptyStateHeading(): string
    {
        return 'Nessun prodotto';
    }

    public function getEmptyStateDescription(): string
    {
        return 'Aggiungi il primo prodotto per iniziare a vendere.';
    }

    public function getEmptyStateIcon(): string
    {
        return 'heroicon-o-shopping-bag';
    }
}
