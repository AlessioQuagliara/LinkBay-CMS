<?php

namespace App\Filament\Tenant\Resources;

use App\Filament\Tenant\Resources\DiscountCodeResource\Pages;
use App\Models\Tenant\DiscountCode;
use Filament\Forms;
use Filament\Schemas\Schema;

use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Support\Str;

class DiscountCodeResource extends Resource
{
    protected static ?string $model = DiscountCode::class;
    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-tag';
    protected static string|\UnitEnum|null $navigationGroup = 'Marketing';
    protected static ?string $modelLabel = 'Codice sconto';
    protected static ?string $pluralModelLabel = 'Codici sconto';

    public static function form(Schema $schema): Schema
    {
        return $schema->schema([
            Forms\Components\TextInput::make('code')
                ->label('Codice')
                ->required()
                ->unique(DiscountCode::class, 'code', ignoreRecord: true)
                ->formatStateUsing(fn ($state) => strtoupper($state ?? ''))
                ->dehydrateStateUsing(fn ($state) => strtoupper($state))
                ->suffixAction(
                    Forms\Components\Actions\Action::make('generate')
                        ->label('Genera')
                        ->icon('heroicon-o-arrow-path')
                        ->action(fn (Set $set) => $set('code', strtoupper(Str::random(8))))
                ),
            Forms\Components\Select::make('type')
                ->label('Tipo')
                ->options([
                    'percentage' => 'Percentuale (%)',
                    'fixed' => 'Importo fisso (€)',
                    'free_shipping' => 'Spedizione gratuita',
                ])
                ->required()
                ->live()
                ->default('percentage'),
            Forms\Components\TextInput::make('value')
                ->label('Valore')
                ->numeric()
                ->required()
                ->visible(fn (Get $get) => $get('type') !== 'free_shipping'),
            Forms\Components\TextInput::make('usage_limit')
                ->label('Limite utilizzi')
                ->numeric()
                ->nullable(),
            Forms\Components\TextInput::make('minimum_amount')
                ->label('Importo minimo ordine (€)')
                ->numeric()
                ->prefix('€')
                ->nullable(),
            Forms\Components\DatePicker::make('expires_at')
                ->label('Scade il')
                ->nullable(),
            Forms\Components\Toggle::make('is_active')
                ->label('Attivo')
                ->default(true),
        ])->columns(2);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('code')
                    ->label('Codice')
                    ->searchable()
                    ->copyable()
                    ->copyMessage('Codice copiato!'),
                Tables\Columns\TextColumn::make('type')
                    ->label('Tipo')
                    ->badge()
                    ->formatStateUsing(fn ($state) => match($state) {
                        'percentage' => 'Percentuale',
                        'fixed' => 'Importo fisso',
                        'free_shipping' => 'Spedizione gratis',
                        default => $state,
                    }),
                Tables\Columns\TextColumn::make('value')
                    ->label('Valore')
                    ->formatStateUsing(fn ($state, $record) => match($record->type) {
                        'percentage' => $state . '%',
                        'fixed' => '€' . $state,
                        default => '—',
                    }),
                Tables\Columns\TextColumn::make('usage_info')
                    ->label('Utilizzi')
                    ->state(fn ($record) => $record->used_count . ' / ' . ($record->usage_limit ?? '∞')),
                Tables\Columns\TextColumn::make('expires_at')
                    ->label('Scadenza')
                    ->date('d/m/Y')
                    ->badge()
                    ->color(fn ($record) => $record->expires_at?->isPast() ? 'danger' : 'success')
                    ->default('—'),
                Tables\Columns\ToggleColumn::make('is_active')
                    ->label('Attivo'),
            ])
            ->actions([
                \Filament\Actions\EditAction::make(),
                \Filament\Actions\DeleteAction::make(),
            ])
            ->bulkActions([
                \Filament\Actions\BulkActionGroup::make([
                    \Filament\Actions\DeleteBulkAction::make(),
                ]),
            ]);
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListDiscountCodes::route('/'),
            'create' => Pages\CreateDiscountCodes::route('/create'),
            'edit' => Pages\EditDiscountCodes::route('/{record}/edit'),
        ];
    }
}
