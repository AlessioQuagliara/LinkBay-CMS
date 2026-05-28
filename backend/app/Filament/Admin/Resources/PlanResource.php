<?php

namespace App\Filament\Admin\Resources;

use App\Filament\Admin\Resources\PlanResource\Pages;
use App\Models\Central\Plan;
use Filament\Forms;
use Filament\Schemas\Schema;

use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;

class PlanResource extends Resource
{
    protected static ?string $model = Plan::class;
    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-credit-card';
    protected static string|\UnitEnum|null $navigationGroup = 'Billing';
    protected static ?string $modelLabel = 'Piano';
    protected static ?string $pluralModelLabel = 'Piani';

    public static function form(Schema $schema): Schema
    {
        return $schema->schema([
            Forms\Components\TextInput::make('name')->label('Nome')->required(),
            Forms\Components\TextInput::make('slug')
                ->label('Slug')
                ->required()
                ->unique(Plan::class, 'slug', ignoreRecord: true),
            Forms\Components\TextInput::make('price')
                ->label('Prezzo')
                ->numeric()
                ->prefix('€')
                ->required(),
            Forms\Components\Select::make('billing_interval')
                ->label('Fatturazione')
                ->options(['month' => 'Mensile', 'year' => 'Annuale'])
                ->default('month')
                ->required(),
            Forms\Components\KeyValue::make('features')
                ->label('Feature incluse')
                ->columnSpanFull(),
            Forms\Components\KeyValue::make('limits')
                ->label('Limiti (es. products: 500)')
                ->columnSpanFull(),
            Forms\Components\TextInput::make('stripe_price_id')
                ->label('Stripe Price ID'),
            Forms\Components\Toggle::make('is_active')->label('Attivo')->default(true),
            Forms\Components\TextInput::make('sort_order')->label('Ordinamento')->numeric()->default(0),
        ])->columns(2);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('name')->label('Nome')->sortable(),
                Tables\Columns\TextColumn::make('price')
                    ->label('Prezzo')
                    ->formatStateUsing(fn ($state, $record) => '€' . $state . ' / ' . $record->billing_interval),
                Tables\Columns\TextColumn::make('tenants_count')
                    ->label('Tenant')
                    ->counts('tenants')
                    ->badge()
                    ->color('info'),
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
            'index' => Pages\ListPlans::route('/'),
            'create' => Pages\CreatePlans::route('/create'),
            'edit' => Pages\EditPlans::route('/{record}/edit'),
        ];
    }
}
