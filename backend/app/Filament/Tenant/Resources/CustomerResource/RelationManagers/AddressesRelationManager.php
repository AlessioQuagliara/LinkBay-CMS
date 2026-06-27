<?php

declare(strict_types=1);

namespace App\Filament\Tenant\Resources\CustomerResource\RelationManagers;

use Filament\Forms;
use Filament\Resources\RelationManagers\RelationManager;
use Filament\Schemas\Schema;
use Filament\Tables;
use Filament\Tables\Table;

class AddressesRelationManager extends RelationManager
{
    protected static string $relationship = 'addresses';

    protected static ?string $title = 'Indirizzi';

    protected static ?string $recordTitleAttribute = 'address_line_1';

    public function form(Schema $schema): Schema
    {
        return $schema->schema([
            Forms\Components\TextInput::make('label')
                ->label('Etichetta')
                ->placeholder('Casa, Ufficio…')
                ->maxLength(50),

            Forms\Components\Grid::make(2)->schema([
                Forms\Components\TextInput::make('first_name')
                    ->label('Nome')
                    ->required()
                    ->maxLength(100),
                Forms\Components\TextInput::make('last_name')
                    ->label('Cognome')
                    ->required()
                    ->maxLength(100),
            ]),

            Forms\Components\TextInput::make('company')
                ->label('Azienda')
                ->maxLength(150),

            Forms\Components\TextInput::make('address_line_1')
                ->label('Indirizzo')
                ->required()
                ->maxLength(255)
                ->columnSpanFull(),

            Forms\Components\TextInput::make('address_line_2')
                ->label('Indirizzo (riga 2)')
                ->maxLength(255)
                ->columnSpanFull(),

            Forms\Components\Grid::make(3)->schema([
                Forms\Components\TextInput::make('city')
                    ->label('Città')
                    ->required()
                    ->maxLength(100),
                Forms\Components\TextInput::make('state')
                    ->label('Provincia/Stato')
                    ->maxLength(100),
                Forms\Components\TextInput::make('postal_code')
                    ->label('CAP')
                    ->required()
                    ->maxLength(20),
            ]),

            Forms\Components\Grid::make(2)->schema([
                Forms\Components\TextInput::make('country_code')
                    ->label('Paese (ISO)')
                    ->required()
                    ->maxLength(2)
                    ->placeholder('IT'),
                Forms\Components\TextInput::make('phone')
                    ->label('Telefono')
                    ->maxLength(30),
            ]),

            Forms\Components\Grid::make(2)->schema([
                Forms\Components\Toggle::make('is_default_shipping')
                    ->label('Indirizzo spedizione predefinito'),
                Forms\Components\Toggle::make('is_default_billing')
                    ->label('Indirizzo fatturazione predefinito'),
            ]),
        ]);
    }

    public function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('label')
                    ->label('Etichetta')
                    ->badge()
                    ->color('gray')
                    ->placeholder('—'),
                Tables\Columns\TextColumn::make('address_line_1')
                    ->label('Indirizzo')
                    ->description(fn ($record) => "{$record->city}, {$record->country_code}")
                    ->searchable(),
                Tables\Columns\TextColumn::make('first_name')
                    ->label('Intestatario')
                    ->formatStateUsing(fn ($state, $record) => "{$state} {$record->last_name}"),
                Tables\Columns\IconColumn::make('is_default_shipping')
                    ->label('Spedizione')
                    ->boolean(),
                Tables\Columns\IconColumn::make('is_default_billing')
                    ->label('Fatturazione')
                    ->boolean(),
            ])
            ->headerActions([
                Tables\Actions\CreateAction::make()->label('Aggiungi indirizzo'),
            ])
            ->actions([
                Tables\Actions\EditAction::make(),
                Tables\Actions\DeleteAction::make(),
            ])
            ->emptyStateHeading('Nessun indirizzo salvato');
    }
}
