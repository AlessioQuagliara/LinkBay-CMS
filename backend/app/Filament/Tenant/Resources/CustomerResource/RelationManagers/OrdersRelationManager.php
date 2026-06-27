<?php

declare(strict_types=1);

namespace App\Filament\Tenant\Resources\CustomerResource\RelationManagers;

use App\Filament\Tenant\Resources\OrderResource;
use Filament\Resources\RelationManagers\RelationManager;
use Filament\Schemas\Schema;
use Filament\Tables;
use Filament\Tables\Table;

class OrdersRelationManager extends RelationManager
{
    protected static string $relationship = 'orders';

    protected static ?string $title = 'Ordini';

    protected static ?string $recordTitleAttribute = 'id';

    public function isReadOnly(): bool
    {
        return true;
    }

    public function form(Schema $schema): Schema
    {
        return $schema->schema([]);
    }

    public function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('id')
                    ->label('#')
                    ->sortable()
                    ->fontFamily('mono'),
                Tables\Columns\BadgeColumn::make('status')
                    ->label('Stato')
                    ->colors([
                        'warning' => 'pending',
                        'info' => ['confirmed', 'processing'],
                        'primary' => 'shipped',
                        'success' => 'delivered',
                        'danger' => ['cancelled', 'refunded'],
                    ]),
                Tables\Columns\TextColumn::make('total')
                    ->label('Totale')
                    ->money('EUR')
                    ->sortable(),
                Tables\Columns\TextColumn::make('created_at')
                    ->label('Data')
                    ->date('d/m/Y')
                    ->sortable(),
            ])
            ->defaultSort('created_at', 'desc')
            ->actions([
                Tables\Actions\Action::make('view')
                    ->label('Visualizza')
                    ->icon('heroicon-o-eye')
                    ->url(fn ($record) => OrderResource::getUrl('view', ['record' => $record])),
            ])
            ->emptyStateHeading('Nessun ordine');
    }
}
