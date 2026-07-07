<?php

declare(strict_types=1);

namespace App\Filament\Tenant\Resources\OrderResource\Pages;

use App\Exports\Tenant\OrderExport;
use App\Filament\Tenant\Resources\OrderResource;
use Carbon\Carbon;
use Filament\Actions;
use Filament\Forms;
use Filament\Resources\Pages\ListRecords;
use Symfony\Component\HttpFoundation\StreamedResponse;

class ListOrders extends ListRecords
{
    protected static string $resource = OrderResource::class;

    protected function getHeaderActions(): array
    {
        return [
            Actions\Action::make('export_orders')
                ->label('Esporta ordini')
                ->icon('heroicon-o-arrow-down-tray')
                ->color('gray')
                ->form([
                    Forms\Components\DatePicker::make('from')
                        ->label('Dal')
                        ->native(false),
                    Forms\Components\DatePicker::make('to')
                        ->label('Al')
                        ->native(false),
                ])
                ->action(function (array $data): StreamedResponse {
                    return app(OrderExport::class)->download(
                        from: $data['from'] ? Carbon::parse($data['from']) : null,
                        to: $data['to'] ? Carbon::parse($data['to']) : null,
                    );
                }),
        ];
    }

    public function getEmptyStateHeading(): string
    {
        return 'Nessun ordine';
    }

    public function getEmptyStateDescription(): string
    {
        return 'Gli ordini ricevuti appariranno qui.';
    }

    public function getEmptyStateIcon(): string
    {
        return 'heroicon-o-shopping-cart';
    }
}
