<?php

declare(strict_types=1);

namespace App\Filament\Admin\Resources;

use App\Filament\Admin\Resources\AgencyHealthAlertResource\Pages;
use App\Models\Central\AgencyHealthAlert;
use Filament\Notifications\Notification;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;

class AgencyHealthAlertResource extends Resource
{
    protected static ?string $model = AgencyHealthAlert::class;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-bell-alert';

    protected static string|\UnitEnum|null $navigationGroup = 'Insights';

    protected static ?string $modelLabel = 'Alert';

    protected static ?string $pluralModelLabel = 'Early Warnings';

    protected static ?int $navigationSort = 3;

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('agency.name')
                    ->label('Agency')
                    ->searchable()
                    ->sortable(),

                Tables\Columns\BadgeColumn::make('type')
                    ->label('Tipo')
                    ->formatStateUsing(fn (string $state) => AgencyHealthAlert::TYPES[$state] ?? $state)
                    ->colors([
                        'warning' => AgencyHealthAlert::TYPE_LOW_ACTIVITY,
                        'danger' => AgencyHealthAlert::TYPE_PREMIUM_NOT_USED,
                        'info' => AgencyHealthAlert::TYPE_DESIGN_DROP,
                        'gray' => AgencyHealthAlert::TYPE_MARKETING_PACK_INACTIVE,
                    ]),

                Tables\Columns\BadgeColumn::make('severity')
                    ->label('Severity')
                    ->formatStateUsing(fn (string $state) => AgencyHealthAlert::SEVERITIES[$state] ?? $state)
                    ->colors([
                        'success' => AgencyHealthAlert::SEVERITY_LOW,
                        'warning' => AgencyHealthAlert::SEVERITY_MEDIUM,
                        'danger' => AgencyHealthAlert::SEVERITY_HIGH,
                    ]),

                Tables\Columns\TextColumn::make('detected_at')
                    ->label('Rilevato il')
                    ->dateTime('d/m/Y H:i')
                    ->sortable(),

                Tables\Columns\TextColumn::make('resolved_at')
                    ->label('Stato')
                    ->formatStateUsing(fn ($state) => $state ? 'Risolto' : 'Aperto')
                    ->badge()
                    ->color(fn ($state) => $state ? 'success' : 'warning'),
            ])
            ->defaultSort('detected_at', 'desc')
            ->filters([
                Tables\Filters\SelectFilter::make('type')
                    ->label('Tipo')
                    ->options(AgencyHealthAlert::TYPES),

                Tables\Filters\SelectFilter::make('severity')
                    ->label('Severity')
                    ->options(AgencyHealthAlert::SEVERITIES),

                Tables\Filters\SelectFilter::make('stato')
                    ->label('Stato')
                    ->options(['open' => 'Aperto', 'resolved' => 'Risolto'])
                    ->query(fn ($query, array $data) => match ($data['value'] ?? null) {
                        'open' => $query->whereNull('resolved_at'),
                        'resolved' => $query->whereNotNull('resolved_at'),
                        default => $query,
                    }),
            ])
            ->actions([
                Tables\Actions\Action::make('resolve')
                    ->label('Risolvi')
                    ->icon('heroicon-o-check-circle')
                    ->color('success')
                    ->visible(fn (AgencyHealthAlert $record) => $record->isOpen())
                    ->requiresConfirmation()
                    ->modalHeading('Segna come risolto')
                    ->modalDescription('L\'alert verrà chiuso. Se le condizioni tornano critiche, un nuovo alert verrà creato al prossimo ciclo.')
                    ->action(function (AgencyHealthAlert $record): void {
                        $record->resolve();
                        Notification::make()->title('Alert risolto')->success()->send();
                    }),

                Tables\Actions\Action::make('view_agency')
                    ->label('Vedi Agency')
                    ->icon('heroicon-o-building-office-2')
                    ->color('gray')
                    ->url(fn (AgencyHealthAlert $record) => AgencyResource::getUrl('edit', ['record' => $record->agency_id]))
                    ->openUrlInNewTab(),
            ])
            ->emptyStateHeading('Nessun alert attivo')
            ->emptyStateDescription('Esegui php artisan agency:health-alerts per valutare le agenzie.')
            ->emptyStateIcon('heroicon-o-bell-slash');
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListAgencyHealthAlerts::route('/'),
        ];
    }
}
