<?php

namespace App\Filament\Tenant\Widgets;

use App\Models\Tenant\Order;
use Filament\Tables;
use Filament\Tables\Table;
use Filament\Widgets\TableWidget as BaseWidget;

class LatestOrdersWidget extends BaseWidget
{
    protected static ?int $sort = 3;
    protected int|string|array $columnSpan = 'full';
    protected static ?string $heading = 'Ultimi ordini';

    public function table(Table $table): Table
    {
        return $table
            ->query(Order::with('customer')->latest()->limit(8))
            ->columns([
                Tables\Columns\TextColumn::make('id')
                    ->label('#')
                    ->formatStateUsing(fn ($state) => '#' . str_pad($state, 4, '0', STR_PAD_LEFT)),
                Tables\Columns\TextColumn::make('customer.name')->label('Cliente'),
                Tables\Columns\TextColumn::make('total')->label('Totale')->money('EUR'),
                Tables\Columns\TextColumn::make('status')
                    ->label('Stato')
                    ->badge()
                    ->color(fn (string $state) => match($state) {
                        'pending' => 'gray',
                        'confirmed' => 'info',
                        'processing' => 'warning',
                        'shipped' => 'primary',
                        'delivered' => 'success',
                        'cancelled' => 'danger',
                        default => 'gray',
                    }),
                Tables\Columns\TextColumn::make('created_at')
                    ->label('Data')
                    ->dateTime('d/m/Y H:i'),
            ])
            ->actions([
                \Filament\Actions\Action::make('view')
                    ->label('Vedi')
                    ->url(fn (Order $record) => route('filament.tenant.resources.orders.view', $record))
                    ->icon('heroicon-o-eye'),
            ]);
    }
}
