<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources;

use App\Filament\Agency\Resources\AgencyClientResource\Pages;
use App\Filament\Agency\Resources\AgencyClientResource\RelationManagers;
use App\Models\Central\AgencyClient;
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
                            'active'     => 'Attivo',
                            'suspended'  => 'Sospeso',
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
                        'active'     => 'success',
                        'suspended'  => 'warning',
                        'offboarded' => 'gray',
                        default      => 'gray',
                    })
                    ->formatStateUsing(fn (string $state) => match ($state) {
                        'active'     => 'Attivo',
                        'suspended'  => 'Sospeso',
                        'offboarded' => 'Offboarded',
                        default      => $state,
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
                        'active'     => 'Attivo',
                        'suspended'  => 'Sospeso',
                        'offboarded' => 'Offboarded',
                    ]),
            ])
            ->actions([
                \Filament\Actions\EditAction::make()->label('Dettaglio'),
                \Filament\Actions\Action::make('suspend')
                    ->label('Sospendi')
                    ->icon('heroicon-o-pause-circle')
                    ->color('warning')
                    ->requiresConfirmation()
                    ->visible(fn (AgencyClient $record) => $record->status === 'active')
                    ->action(fn (AgencyClient $record) => $record->update(['status' => 'suspended'])),
                \Filament\Actions\Action::make('reactivate')
                    ->label('Riattiva')
                    ->icon('heroicon-o-play-circle')
                    ->color('success')
                    ->visible(fn (AgencyClient $record) => $record->status !== 'active')
                    ->action(fn (AgencyClient $record) => $record->update(['status' => 'active'])),
                \Filament\Actions\DeleteAction::make(),
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
            'index'  => Pages\ListAgencyClients::route('/'),
            'create' => Pages\CreateAgencyClient::route('/create'),
            'edit'   => Pages\EditAgencyClient::route('/{record}/edit'),
        ];
    }
}
