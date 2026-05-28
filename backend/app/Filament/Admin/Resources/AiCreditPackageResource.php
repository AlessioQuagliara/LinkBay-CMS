<?php

namespace App\Filament\Admin\Resources;

use App\Filament\Admin\Resources\AiCreditPackageResource\Pages;
use App\Models\Central\AiCreditPackage;
use Filament\Forms;
use Filament\Resources\Resource;
use Filament\Schemas\Schema;
use Filament\Tables;
use Filament\Tables\Table;

class AiCreditPackageResource extends Resource
{
    protected static ?string $model = AiCreditPackage::class;
    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-sparkles';
    protected static string|\UnitEnum|null $navigationGroup = 'AI Credits';
    protected static ?string $modelLabel = 'Pacchetto AI';
    protected static ?string $pluralModelLabel = 'Pacchetti AI';

    public static function form(Schema $schema): Schema
    {
        return $schema->schema([
            Forms\Components\TextInput::make('name')->label('Nome')->required(),
            Forms\Components\TextInput::make('credits')
                ->label('Crediti')
                ->numeric()
                ->required()
                ->helperText('Es: 10000 = 10K crediti'),
            Forms\Components\TextInput::make('price_cents')
                ->label('Prezzo (centesimi)')
                ->numeric()
                ->required()
                ->helperText('Es: 990 = €9,90')
                ->suffix('¢'),
            Forms\Components\TextInput::make('stripe_price_id')
                ->label('Stripe Price ID')
                ->placeholder('price_xxx'),
            Forms\Components\Toggle::make('is_active')->label('Attivo')->default(true),
            Forms\Components\TextInput::make('sort_order')->label('Ordinamento')->numeric()->default(0),
        ])->columns(2);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('name')->label('Nome')->sortable(),
                Tables\Columns\TextColumn::make('credits')
                    ->label('Crediti')
                    ->formatStateUsing(fn ($state) => number_format($state) . ' cr'),
                Tables\Columns\TextColumn::make('price_cents')
                    ->label('Prezzo')
                    ->formatStateUsing(fn ($state) => '€' . number_format($state / 100, 2, ',', '.')),
                Tables\Columns\TextColumn::make('price_per_1k')
                    ->label('€/1K cr')
                    ->state(fn ($record) => $record->credits > 0
                        ? '€' . number_format(($record->price_cents / 100) / ($record->credits / 1000), 3, ',', '.')
                        : '—'),
                Tables\Columns\ToggleColumn::make('is_active')->label('Attivo'),
                Tables\Columns\TextColumn::make('sort_order')->label('Ordine')->sortable(),
            ])
            ->reorderable('sort_order')
            ->actions([
                \Filament\Actions\EditAction::make(),
                \Filament\Actions\DeleteAction::make(),
            ]);
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListAiCreditPackages::route('/'),
            'create' => Pages\CreateAiCreditPackage::route('/create'),
            'edit' => Pages\EditAiCreditPackage::route('/{record}/edit'),
        ];
    }
}
