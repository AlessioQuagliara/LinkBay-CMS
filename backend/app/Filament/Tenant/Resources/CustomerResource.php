<?php

declare(strict_types=1);

namespace App\Filament\Tenant\Resources;

use App\Filament\Tenant\Resources\CustomerResource\Pages;
use App\Filament\Tenant\Resources\CustomerResource\RelationManagers\AddressesRelationManager;
use App\Filament\Tenant\Resources\CustomerResource\RelationManagers\OrdersRelationManager;
use App\Filament\Tenant\Resources\CustomerResource\RelationManagers\WishlistRelationManager;
use App\Models\Tenant\Customer;
use Filament\Actions\DeleteAction;
use Filament\Actions\EditAction;
use Filament\Actions\ViewAction;
use Filament\Forms;
use Filament\Infolists;
use Filament\Notifications\Notification;
use Filament\Resources\Resource;
use Filament\Schemas\Components\Section;
use Filament\Schemas\Schema;
use Filament\Tables;
use Filament\Tables\Table;

class CustomerResource extends Resource
{
    protected static ?string $model = Customer::class;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-users';

    protected static string|\UnitEnum|null $navigationGroup = 'Vendite';

    protected static ?string $modelLabel = 'Cliente';

    protected static ?string $pluralModelLabel = 'Clienti';

    protected static ?int $navigationSort = 2;

    public static function form(Schema $schema): Schema
    {
        return $schema->schema([
            Forms\Components\TextInput::make('name')->label('Nome')->required(),
            Forms\Components\TextInput::make('email')->label('Email')->email()->required()
                ->unique(Customer::class, 'email', ignoreRecord: true),
            Forms\Components\TextInput::make('phone')->label('Telefono'),

            Forms\Components\Select::make('status')
                ->label('Stato')
                ->options(['active' => 'Attivo', 'disabled' => 'Disabilitato'])
                ->default('active')
                ->required(),

            Forms\Components\Toggle::make('accepts_marketing')
                ->label('Accetta marketing'),

            Section::make('Indirizzo (legacy JSON)')
                ->schema([
                    Forms\Components\TextInput::make('address.street')->label('Via / N. civico'),
                    Forms\Components\TextInput::make('address.city')->label('Città'),
                    Forms\Components\TextInput::make('address.zip')->label('CAP'),
                    Forms\Components\TextInput::make('address.province')->label('Provincia')->maxLength(2),
                    Forms\Components\TextInput::make('address.country')->label('Paese')->default('IT'),
                ])->columns(2)->collapsible()->collapsed(),

            Forms\Components\Textarea::make('notes')->label('Note interne')->rows(3)->columnSpanFull(),
            Forms\Components\TagsInput::make('tags')->label('Tag'),
        ])->columns(2);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('name')
                    ->label('Nome')
                    ->searchable()
                    ->sortable(),
                Tables\Columns\TextColumn::make('email')
                    ->label('Email')
                    ->searchable(),
                Tables\Columns\TextColumn::make('phone')
                    ->label('Telefono')
                    ->toggleable(),
                Tables\Columns\BadgeColumn::make('status')
                    ->label('Stato')
                    ->colors(['success' => 'active', 'danger' => 'disabled']),
                Tables\Columns\IconColumn::make('accepts_marketing')
                    ->label('Marketing')
                    ->boolean()
                    ->toggleable(),
                Tables\Columns\TextColumn::make('total_spent')
                    ->label('Speso')
                    ->money('EUR')
                    ->sortable(),
                Tables\Columns\TextColumn::make('orders_count')
                    ->label('Ordini')
                    ->badge()
                    ->color('info'),
                Tables\Columns\TextColumn::make('last_login_at')
                    ->label('Ultimo accesso')
                    ->since()
                    ->toggleable(),
                Tables\Columns\TextColumn::make('created_at')
                    ->label('Registrato')
                    ->date('d/m/Y')
                    ->sortable(),
            ])
            ->filters([
                Tables\Filters\SelectFilter::make('status')
                    ->label('Stato')
                    ->options(['active' => 'Attivo', 'disabled' => 'Disabilitato']),
                Tables\Filters\TernaryFilter::make('accepts_marketing')
                    ->label('Accetta marketing'),
                Tables\Filters\Filter::make('country')
                    ->form([
                        Forms\Components\TextInput::make('country_code')
                            ->label('Paese (ISO)')
                            ->maxLength(2)
                            ->placeholder('IT'),
                    ])
                    ->query(fn ($query, array $data) => $query->when(
                        $data['country_code'] ?? null,
                        fn ($q, $code) => $q->whereHas(
                            'addresses',
                            fn ($a) => $a->where('country_code', strtoupper($code))
                        )
                    )
                    ),
            ])
            ->actions([
                EditAction::make(),
                ViewAction::make(),
                DeleteAction::make(),
            ])
            ->bulkActions([
                Tables\Actions\BulkActionGroup::make([
                    Tables\Actions\DeleteBulkAction::make(),
                    Tables\Actions\BulkAction::make('send_marketing_email')
                        ->label('Invia email marketing')
                        ->icon('heroicon-o-envelope')
                        ->requiresConfirmation()
                        ->deselectRecordsAfterCompletion()
                        ->before(function ($records, Tables\Actions\BulkAction $action): void {
                            $hasNonConsent = $records->contains(
                                fn (Customer $c) => ! $c->accepts_marketing
                            );

                            if ($hasNonConsent) {
                                $action->failWithoutNotifying();
                                Notification::make()
                                    ->title('Attenzione')
                                    ->body('Alcuni clienti selezionati non hanno acconsentito al marketing.')
                                    ->warning()
                                    ->send();
                            }
                        })
                        ->action(function ($records): void {
                            // TODO: dispatch batch marketing email job
                        }),
                ]),
            ])
            ->defaultSort('created_at', 'desc');
    }

    public static function infolist(Schema $schema): Schema
    {
        return $schema->schema([
            Infolists\Components\Section::make('Anagrafica')
                ->schema([
                    Infolists\Components\TextEntry::make('name')->label('Nome'),
                    Infolists\Components\TextEntry::make('email')->label('Email'),
                    Infolists\Components\TextEntry::make('phone')->label('Telefono'),
                    Infolists\Components\BadgeEntry::make('status')
                        ->label('Stato')
                        ->colors(['success' => 'active', 'danger' => 'disabled']),
                    Infolists\Components\IconEntry::make('accepts_marketing')
                        ->label('Accetta marketing')
                        ->boolean(),
                    Infolists\Components\TextEntry::make('notes')->label('Note')->columnSpanFull(),
                ])->columns(3),

            Infolists\Components\Section::make('Statistiche')
                ->schema([
                    Infolists\Components\TextEntry::make('total_spent')
                        ->label('Totale speso')
                        ->money('EUR'),
                    Infolists\Components\TextEntry::make('orders_count')
                        ->label('Numero ordini'),
                    Infolists\Components\TextEntry::make('last_login_at')
                        ->label('Ultimo accesso')
                        ->dateTime('d/m/Y H:i')
                        ->placeholder('Mai'),
                    Infolists\Components\TextEntry::make('email_verified_at')
                        ->label('Email verificata')
                        ->dateTime('d/m/Y')
                        ->placeholder('Non verificata'),
                ])->columns(4),

            Infolists\Components\Section::make('Indirizzo (legacy JSON)')
                ->schema([
                    Infolists\Components\TextEntry::make('address.street')->label('Via'),
                    Infolists\Components\TextEntry::make('address.city')->label('Città'),
                    Infolists\Components\TextEntry::make('address.zip')->label('CAP'),
                    Infolists\Components\TextEntry::make('address.country')->label('Paese'),
                ])->columns(4)->collapsible()->collapsed(),
        ]);
    }

    public static function getRelationManagers(): array
    {
        return [
            AddressesRelationManager::class,
            OrdersRelationManager::class,
            WishlistRelationManager::class,
        ];
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListCustomers::route('/'),
            'create' => Pages\CreateCustomer::route('/create'),
            'edit' => Pages\EditCustomer::route('/{record}/edit'),
            'view' => Pages\ViewCustomer::route('/{record}'),
        ];
    }
}
