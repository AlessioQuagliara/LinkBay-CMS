<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources;

use App\Filament\Agency\Resources\AgencyClientResource\Pages;
use App\Filament\Agency\Resources\AgencyClientResource\RelationManagers;
use App\Models\Central\AgencyClient;
use App\Models\Central\AgencyClientContact;
use App\Services\ClientInviteService;
use Filament\Actions\Action;
use Filament\Actions\DeleteAction;
use Filament\Actions\EditAction;
use Filament\Forms;
use Filament\Notifications\Notification;
use Filament\Resources\Resource;
use Filament\Schemas\Components\Section;
use Filament\Schemas\Schema;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;

class AgencyClientResource extends Resource
{
    protected static ?string $model = AgencyClient::class;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-users';

    protected static ?string $modelLabel = 'Cliente';

    protected static ?string $pluralModelLabel = 'Clienti';

    protected static ?int $navigationSort = 1;

    // ── Security: scope every query to the current agency ────────────────────

    public static function getEloquentQuery(): Builder
    {
        $agency = app()->has('current_agency') ? app('current_agency') : null;

        return parent::getEloquentQuery()
            ->when(
                $agency,
                fn (Builder $q) => $q->where('agency_id', $agency->id),
                fn (Builder $q) => $q->whereRaw('1=0')
            );
    }

    // ── Form ─────────────────────────────────────────────────────────────────

    public static function form(Schema $schema): Schema
    {
        return $schema->schema([
            Section::make('Anagrafica')
                ->schema([
                    Forms\Components\TextInput::make('name')
                        ->label('Nome cliente / azienda')
                        ->required()
                        ->maxLength(255),
                    Forms\Components\TextInput::make('legal_name')
                        ->label('Ragione sociale')
                        ->maxLength(255),
                    Forms\Components\TextInput::make('vat_number')
                        ->label('P.IVA / C.F.')
                        ->maxLength(30),
                    Forms\Components\TextInput::make('country')
                        ->label('Paese (ISO 2)')
                        ->maxLength(2)
                        ->placeholder('IT'),
                    Forms\Components\TextInput::make('billing_email')
                        ->label('Email fatturazione')
                        ->email()
                        ->maxLength(255),
                    Forms\Components\Select::make('status')
                        ->label('Stato')
                        ->options([
                            'active' => 'Attivo',
                            'suspended' => 'Sospeso',
                            'offboarded' => 'Offboarded',
                        ])
                        ->default('active')
                        ->required(),
                ])->columns(2),

            Section::make('Note interne')
                ->schema([
                    Forms\Components\Textarea::make('notes')
                        ->label('Note')
                        ->rows(4)
                        ->maxLength(4000),
                ])->collapsed(fn ($record) => $record?->notes === null),
        ]);
    }

    // ── Table ────────────────────────────────────────────────────────────────

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('name')
                    ->label('Cliente')
                    ->searchable()
                    ->sortable()
                    ->weight('medium'),
                Tables\Columns\TextColumn::make('billing_email')
                    ->label('Email')
                    ->searchable()
                    ->placeholder('—'),
                Tables\Columns\TextColumn::make('status')
                    ->label('Stato')
                    ->badge()
                    ->color(fn (string $state) => match ($state) {
                        'active' => 'success',
                        'suspended' => 'warning',
                        'offboarded' => 'gray',
                        default => 'gray',
                    })
                    ->formatStateUsing(fn (string $state) => match ($state) {
                        'active' => 'Attivo',
                        'suspended' => 'Sospeso',
                        'offboarded' => 'Offboarded',
                        default => $state,
                    }),
                Tables\Columns\TextColumn::make('stores_count')
                    ->label('Store')
                    ->counts('stores')
                    ->badge()
                    ->color('primary'),
                Tables\Columns\TextColumn::make('created_at')
                    ->label('Creato')
                    ->date('d/m/Y')
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
            ])
            ->defaultSort('name')
            ->filters([
                Tables\Filters\SelectFilter::make('status')
                    ->options([
                        'active' => 'Attivo',
                        'suspended' => 'Sospeso',
                        'offboarded' => 'Offboarded',
                    ]),
            ])
            ->actions([
                EditAction::make()->label('Dettaglio'),
                Action::make('invite_owner')
                    ->label('Invita store owner')
                    ->icon('heroicon-o-envelope')
                    ->color('primary')
                    ->visible(fn (AgencyClient $record) => $record->stores()->exists())
                    ->form(function (AgencyClient $record): array {
                        $stores = $record->stores()->get();
                        $fields = [
                            Forms\Components\TextInput::make('email')
                                ->label('Email store owner')
                                ->email()
                                ->required(),
                        ];
                        if ($stores->count() > 1) {
                            $fields[] = Forms\Components\Select::make('tenant_id')
                                ->label('Store')
                                ->options($stores->pluck('name', 'id'))
                                ->required();
                        }

                        return $fields;
                    })
                    ->action(function (AgencyClient $record, array $data): void {
                        $tenant = isset($data['tenant_id'])
                            ? $record->stores()->find($data['tenant_id'])
                            : $record->stores()->first();

                        if (! $tenant) {
                            Notification::make()->title('Nessuno store disponibile')->danger()->send();

                            return;
                        }

                        $contact = AgencyClientContact::firstOrCreate(
                            ['agency_client_id' => $record->id, 'email' => $data['email']],
                            ['name' => $data['email'], 'can_access_tenant' => false],
                        );

                        app(ClientInviteService::class)->generateInvite($contact, $tenant);

                        Notification::make()
                            ->title('Invito inviato a '.$data['email'])
                            ->body('Il link è valido per 72 ore.')
                            ->success()
                            ->send();
                    }),
                Action::make('access_store')
                    ->label('Accedi al pannello')
                    ->icon('heroicon-o-arrow-top-right-on-square')
                    ->color('gray')
                    ->url(function (AgencyClient $record): ?string {
                        $tenant = $record->stores()->first();
                        if (! $tenant) {
                            return null;
                        }
                        $scheme = app()->isProduction() ? 'https' : 'http';

                        return "{$scheme}://{$tenant->id}.".config('app.store_domain').'/admin';
                    })
                    ->openUrlInNewTab()
                    ->visible(fn (AgencyClient $record) => $record->stores()->exists()),
                Action::make('suspend')
                    ->label('Sospendi')
                    ->icon('heroicon-o-pause-circle')
                    ->color('warning')
                    ->requiresConfirmation()
                    ->visible(fn (AgencyClient $record) => $record->status === 'active')
                    ->action(fn (AgencyClient $record) => $record->update(['status' => 'suspended'])),
                Action::make('reactivate')
                    ->label('Riattiva')
                    ->icon('heroicon-o-play-circle')
                    ->color('success')
                    ->visible(fn (AgencyClient $record) => $record->status !== 'active')
                    ->action(fn (AgencyClient $record) => $record->update(['status' => 'active'])),
                DeleteAction::make(),
            ])
            ->emptyStateHeading('Nessun cliente')
            ->emptyStateDescription('Crea il primo cliente per iniziare a gestire i progetti della tua agency.')
            ->emptyStateIcon('heroicon-o-users');
    }

    // ── Relations ────────────────────────────────────────────────────────────

    public static function getRelations(): array
    {
        return [
            RelationManagers\ContactsRelationManager::class,
            RelationManagers\StoresRelationManager::class,
        ];
    }

    // ── Pages ────────────────────────────────────────────────────────────────

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListAgencyClients::route('/'),
            'create' => Pages\CreateAgencyClient::route('/create'),
            'edit' => Pages\EditAgencyClient::route('/{record}/edit'),
        ];
    }
}
