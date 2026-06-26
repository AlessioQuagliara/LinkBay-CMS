<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources\AgencyClientResource\RelationManagers;

use App\Http\Controllers\Tenant\TenantImpersonateController;
use App\Models\Central\Tenant;
use Filament\Actions\Action;
use Filament\Actions\AssociateAction;
use Filament\Actions\BulkActionGroup;
use Filament\Actions\DissociateAction;
use Filament\Actions\DissociateBulkAction;
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
                    ->formatStateUsing(fn (string $state) => $state.'.'.config('app.store_domain')),
                Tables\Columns\TextColumn::make('status')
                    ->label('Stato')
                    ->badge()
                    ->color(fn (string $state) => $state === 'active' ? 'success' : 'warning')
                    ->formatStateUsing(fn (string $state) => $state === 'active' ? 'Attivo' : 'Sospeso'),
            ])
            ->headerActions([
                AssociateAction::make()
                    ->label('Associa store')
                    ->recordSelectOptionsQuery(function (Builder $query) {
                        // Only show stores from this client's agency that aren't yet linked to any client
                        return $query
                            ->where('agency_id', $this->ownerRecord->agency_id)
                            ->whereNull('agency_client_id');
                    }),
            ])
            ->actions([
                Action::make('access_store')
                    ->label('Accedi come cliente')
                    ->icon('heroicon-o-identification')
                    ->color('primary')
                    ->url(function (Tenant $record): string {
                        $token = TenantImpersonateController::generateToken(
                            auth()->user()->email,
                            $record->id,
                        );
                        $scheme = app()->isProduction() ? 'https' : 'http';

                        return "{$scheme}://{$record->id}.".config('app.store_domain')."/_impersonate/{$token}";
                    })
                    ->openUrlInNewTab(),
                Action::make('access_panel')
                    ->label('Apri pannello')
                    ->icon('heroicon-o-arrow-top-right-on-square')
                    ->color('gray')
                    ->url(function (Tenant $record): string {
                        $scheme = app()->isProduction() ? 'https' : 'http';

                        return "{$scheme}://{$record->id}.".config('app.store_domain').'/admin';
                    })
                    ->openUrlInNewTab(),
                DissociateAction::make()->label('Rimuovi'),
            ])
            ->bulkActions([
                BulkActionGroup::make([
                    DissociateBulkAction::make(),
                ]),
            ])
            ->emptyStateHeading('Nessuno store associato')
            ->emptyStateDescription('Associa uno store esistente a questo cliente.')
            ->emptyStateIcon('heroicon-o-shopping-bag');
    }
}
