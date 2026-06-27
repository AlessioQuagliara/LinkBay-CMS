<?php

declare(strict_types=1);

namespace App\Filament\Tenant\Resources\CustomerResource\RelationManagers;

use Filament\Resources\RelationManagers\RelationManager;
use Filament\Schemas\Schema;
use Filament\Tables;
use Filament\Tables\Table;

class WishlistRelationManager extends RelationManager
{
    protected static string $relationship = 'wishlistProducts';

    protected static ?string $title = 'Wishlist';

    protected static ?string $recordTitleAttribute = 'name';

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
                Tables\Columns\TextColumn::make('name')
                    ->label('Prodotto')
                    ->searchable(),
                Tables\Columns\TextColumn::make('sku')
                    ->label('SKU')
                    ->fontFamily('mono')
                    ->color('gray'),
                Tables\Columns\TextColumn::make('price')
                    ->label('Prezzo')
                    ->money('EUR'),
                Tables\Columns\BadgeColumn::make('status')
                    ->label('Stato')
                    ->colors([
                        'success' => 'active',
                        'danger' => 'archived',
                        'warning' => 'draft',
                    ]),
                Tables\Columns\TextColumn::make('pivot.created_at')
                    ->label('Aggiunto il')
                    ->date('d/m/Y'),
            ])
            ->defaultSort('pivot_created_at', 'desc')
            ->emptyStateHeading('Wishlist vuota');
    }
}
