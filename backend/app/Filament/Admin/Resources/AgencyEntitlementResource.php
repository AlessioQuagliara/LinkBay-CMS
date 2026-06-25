<?php

declare(strict_types=1);

namespace App\Filament\Admin\Resources;

use App\Filament\Admin\Resources\AgencyEntitlementResource\Pages;
use App\Models\Central\AgencyEntitlement;
use App\Models\Central\AuditEvent;
use App\Models\Central\PluginCatalogItem;
use App\Services\AuditEventService;
use Filament\Forms;
use Filament\Notifications\Notification;
use Filament\Resources\Resource;
use Filament\Schemas\Schema;
use Filament\Tables;
use Filament\Tables\Table;

class AgencyEntitlementResource extends Resource
{
    protected static ?string $model = AgencyEntitlement::class;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-key';

    protected static string|\UnitEnum|null $navigationGroup = 'Marketplace';

    protected static ?string $modelLabel = 'Entitlement';

    protected static ?string $pluralModelLabel = 'Entitlements';

    public static function form(Schema $schema): Schema
    {
        return $schema->schema([
            Forms\Components\Select::make('agency_id')
                ->label('Agency')
                ->relationship('agency', 'name')
                ->searchable()
                ->preload()
                ->required(),
            Forms\Components\Select::make('catalog_item_id')
                ->label('Catalog Item')
                ->options(fn () => PluginCatalogItem::active()->pluck('name', 'id'))
                ->searchable()
                ->required(),
            Forms\Components\Select::make('source')
                ->label('Sorgente')
                ->options(AgencyEntitlement::SOURCES)
                ->default(AgencyEntitlement::SOURCE_MANUAL)
                ->required(),
            Forms\Components\Select::make('status')
                ->label('Stato')
                ->options(AgencyEntitlement::STATUSES)
                ->default(AgencyEntitlement::STATUS_ACTIVE)
                ->required(),
            Forms\Components\DateTimePicker::make('starts_at')
                ->label('Inizio validità')
                ->nullable()
                ->helperText('Lascia vuoto per attivare subito.'),
            Forms\Components\DateTimePicker::make('ends_at')
                ->label('Scadenza')
                ->nullable()
                ->helperText('Lascia vuoto per validità illimitata.'),
            Forms\Components\KeyValue::make('metadata')
                ->label('Metadata')
                ->columnSpanFull(),
        ])->columns(2);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('agency.name')
                    ->label('Agency')
                    ->searchable()
                    ->sortable(),
                Tables\Columns\TextColumn::make('catalogItem.code')
                    ->label('Feature Code')
                    ->fontFamily('mono')
                    ->searchable(),
                Tables\Columns\TextColumn::make('catalogItem.name')
                    ->label('Catalog Item')
                    ->searchable(),
                Tables\Columns\BadgeColumn::make('source')
                    ->label('Sorgente')
                    ->formatStateUsing(fn (string $state) => AgencyEntitlement::SOURCES[$state] ?? $state)
                    ->colors([
                        'primary' => AgencyEntitlement::SOURCE_PLAN,
                        'info' => AgencyEntitlement::SOURCE_MANUAL,
                        'success' => AgencyEntitlement::SOURCE_PROMO,
                        'warning' => AgencyEntitlement::SOURCE_LICENSE,
                    ]),
                Tables\Columns\BadgeColumn::make('status')
                    ->label('Stato')
                    ->formatStateUsing(fn (string $state) => AgencyEntitlement::STATUSES[$state] ?? $state)
                    ->colors([
                        'success' => AgencyEntitlement::STATUS_ACTIVE,
                        'gray' => AgencyEntitlement::STATUS_EXPIRED,
                        'danger' => AgencyEntitlement::STATUS_REVOKED,
                    ]),
                Tables\Columns\TextColumn::make('ends_at')
                    ->label('Scadenza')
                    ->dateTime('d/m/Y')
                    ->placeholder('Illimitata')
                    ->sortable(),
                Tables\Columns\TextColumn::make('updated_at')
                    ->label('Modificato')
                    ->dateTime('d/m/Y H:i')
                    ->sortable(),
            ])
            ->defaultSort('updated_at', 'desc')
            ->filters([
                Tables\Filters\SelectFilter::make('agency')
                    ->relationship('agency', 'name')
                    ->searchable()
                    ->preload(),
                Tables\Filters\SelectFilter::make('status')
                    ->options(AgencyEntitlement::STATUSES),
                Tables\Filters\SelectFilter::make('source')
                    ->options(AgencyEntitlement::SOURCES),
            ])
            ->actions([
                Tables\Actions\EditAction::make()
                    ->visible(fn (AgencyEntitlement $record) => $record->status === AgencyEntitlement::STATUS_ACTIVE),

                Tables\Actions\Action::make('revoke')
                    ->label('Revoca')
                    ->icon('heroicon-o-x-circle')
                    ->color('danger')
                    ->visible(fn (AgencyEntitlement $record) => $record->status === AgencyEntitlement::STATUS_ACTIVE)
                    ->requiresConfirmation()
                    ->modalHeading('Revoca entitlement')
                    ->modalDescription('La agency perderà immediatamente accesso a questa feature.')
                    ->action(function (AgencyEntitlement $record): void {
                        $record->revoke();

                        app(AuditEventService::class)->log(
                            event: AuditEvent::EVENT_ENTITLEMENT_REVOKED,
                            agencyId: $record->agency_id,
                            subjectType: 'agency_entitlement',
                            subjectId: $record->id,
                            newValues: ['status' => AgencyEntitlement::STATUS_REVOKED, 'code' => $record->catalogItem->code],
                        );

                        Notification::make()->title('Entitlement revocato')->warning()->send();
                    }),

                Tables\Actions\Action::make('reactivate')
                    ->label('Riattiva')
                    ->icon('heroicon-o-arrow-path')
                    ->color('success')
                    ->visible(fn (AgencyEntitlement $record) => in_array($record->status, [AgencyEntitlement::STATUS_REVOKED, AgencyEntitlement::STATUS_EXPIRED]))
                    ->requiresConfirmation()
                    ->action(function (AgencyEntitlement $record): void {
                        $record->update(['status' => AgencyEntitlement::STATUS_ACTIVE]);

                        app(AuditEventService::class)->log(
                            event: AuditEvent::EVENT_ENTITLEMENT_GRANTED,
                            agencyId: $record->agency_id,
                            subjectType: 'agency_entitlement',
                            subjectId: $record->id,
                            newValues: ['status' => AgencyEntitlement::STATUS_ACTIVE, 'code' => $record->catalogItem->code],
                        );

                        Notification::make()->title('Entitlement riattivato')->success()->send();
                    }),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\BulkAction::make('bulk_revoke')
                        ->label('Revoca selezionati')
                        ->icon('heroicon-o-x-circle')
                        ->color('danger')
                        ->requiresConfirmation()
                        ->action(function ($records): void {
                            $audit = app(AuditEventService::class);
                            foreach ($records as $record) {
                                if ($record->status === AgencyEntitlement::STATUS_ACTIVE) {
                                    $record->revoke();
                                    $audit->log(
                                        event: AuditEvent::EVENT_ENTITLEMENT_REVOKED,
                                        agencyId: $record->agency_id,
                                        subjectType: 'agency_entitlement',
                                        subjectId: $record->id,
                                        newValues: ['status' => AgencyEntitlement::STATUS_REVOKED, 'code' => $record->catalogItem->code],
                                    );
                                }
                            }
                            Notification::make()->title('Entitlements revocati')->warning()->send();
                        }),
                ]),
            ])
            ->emptyStateHeading('Nessun entitlement')
            ->emptyStateDescription('Assegna una feature premium a una agency.')
            ->emptyStateIcon('heroicon-o-key');
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListAgencyEntitlements::route('/'),
            'create' => Pages\CreateAgencyEntitlement::route('/create'),
            'edit' => Pages\EditAgencyEntitlement::route('/{record}/edit'),
        ];
    }
}
