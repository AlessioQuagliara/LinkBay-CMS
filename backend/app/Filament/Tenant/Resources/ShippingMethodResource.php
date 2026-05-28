<?php

namespace App\Filament\Tenant\Resources;

use App\Filament\Tenant\Resources\ShippingMethodResource\Pages;
use App\Models\Tenant\ShippingMethod;
use Filament\Forms;
use Filament\Schemas\Schema;

use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;

class ShippingMethodResource extends Resource
{
    protected static ?string $model = ShippingMethod::class;
    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-truck';
    protected static string|\NITENUM|NULL $NAVIGATIONGROUP = 'Impostazioni';
    protected static ?string $modelLabel = 'Metodo spedizione';
    protected static ?string $pluralModelLabel = 'Metodi spedizione';

    public static function form(Schema $schema): Schema
    {
        return $schema->schema([
            Forms\Components\TextInput::make('name')->label('Nome')->required(),
            Forms\Components\TextInput::make('carrier')->label('Corriere'),
            Forms\Components\TextInput::make('price')
                ->label('Prezzo (€)')
                ->numeric()
                ->required()
                ->prefix('€'),
            Forms\Components\TextInput::make('estimated_days')
                ->label('Giorni stimati')
                ->numeric()
                ->suffix('gg'),
            Forms\Components\KeyValue::make('rules')
                ->label('Regole (es. peso, importo minimo)')
                ->columnSpanFull(),
            Forms\Components\Toggle::make('is_active')
                ->label('Attivo')
                ->default(true),
        ])->columns(2);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('name')->label('Nome')->searchable(),
                Tables\Columns\TextColumn::make('carrier')->label('Corriere'),
                Tables\Columns\TextColumn::make('price')->label('Prezzo')->money('EUR'),
                Tables\Columns\ToggleColumn::make('is_active')->label('Attivo'),
            ])
            ->actions([
                \Filament\Actions\EditAction::make(),
                \Filament\Actions\DeleteAction::make(),
            ]);
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListShippingMethods::route('/'),
            'create' => Pages\CreateShippingMethods::route('/create'),
            'edit' => Pages\EditShippingMethods::route('/{record}/edit'),
        ];
    }
}
