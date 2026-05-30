<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources\AgencyClientResource\RelationManagers;

use App\Models\Central\Tenant;
use Filament\Resources\RelationManagers\RelationManager;
use Filament\Schemas\Schema;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;

class StoresRelationManager extends RelationManager
{
    protected static string $relationship = 'stores';
    protected static ?string $title = 'Store associati';
    protected static ?string $recordTitleAttribute = 'name';

    public function form(Schema $schema): Schema
    {
        // Not used for this relation manager (associate-only, no inline create)
        return $schema->schema([]);
    }

    public function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('name')
                    ->label('Nome store')
                    ->searchable()
                    ->weight('medium'),
                Tables\Columns\TextColumn::make('id')
                    ->label('Subdomain')
                    ->formatStateUsing(fn (string $state) => $state . '.' . config('app.store_domain')),
                Tables\Columns\TextColumn::make('status')
                    ->label('Stato')
                    ->badge()
                    ->color(fn (string $state) => $state === 'active' ? 'success' : 'warning')
                    ->formatStateUsing(fn (string $state) => $state === 'active' ? 'Attivo' : 'Sospeso'),
            ])
            ->headerActions([
                \Filament\Actions\AssociateAction::make()
                    ->label('Associa store')
                    ->recordSelectOptionsQuery(function (Builder $query) {
                        // Only show stores from this client's agency that aren't yet linked to any client
                        return $query
                            ->where('agency_id', $this->ownerRecord->agency_id)
                            ->whereNull('agency_client_id');
                    }),
            ])
            ->actions([
                \Filament\Actions\DissociateAction::make()->label('Rimuovi'),
            ])
            ->bulkActions([
                \Filament\Actions\BulkActionGroup::make([
                    \Filament\Actions\DissociateBulkAction::make(),
                ]),
            ])
            ->emptyStateHeading('Nessuno store associato')
            ->emptyStateDescription('Associa uno store esistente a questo cliente.')
            ->emptyStateIcon('heroicon-o-shopping-bag');
    }
}
