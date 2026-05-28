<?php

namespace App\Filament\Tenant\Resources;

use App\Filament\Tenant\Resources\CollectionResource\Pages;
use App\Models\Tenant\Collection;
use Filament\Forms;
use Filament\Schemas\Schema;

use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Support\Str;

class CollectionResource extends Resource
{
    protected static ?string $model = Collection::class;
    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-folder';
    protected static string|\UnitEnum|null $navigationGroup = 'Catalogo';
    protected static ?string $modelLabel = 'Collezione';
    protected static ?string $pluralModelLabel = 'Collezioni';
    protected static ?int $navigationSort = 2;

    public static function form(Schema $schema): Schema
    {
        return $schema->schema([
            Forms\Components\TextInput::make('name')
                ->label('Nome')
                ->required()
                ->maxLength(255)
                ->live(onBlur: true)
                ->afterStateUpdated(fn ($state, Set $set) =>
                    $set('slug', Str::slug($state))
                ),
            Forms\Components\TextInput::make('slug')
                ->label('Slug')
                ->required()
                ->unique(Collection::class, 'slug', ignoreRecord: true),
            Forms\Components\Select::make('parent_id')
                ->label('Collezione padre')
                ->relationship('parent', 'name')
                ->searchable()
                ->preload()
                ->nullable(),
            Forms\Components\Textarea::make('description')
                ->label('Descrizione')
                ->rows(3)
                ->columnSpanFull(),
            Forms\Components\Toggle::make('is_active')
                ->label('Attiva')
                ->default(true),
            Forms\Components\TextInput::make('sort_order')
                ->label('Ordinamento')
                ->numeric()
                ->default(0),
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
                Tables\Columns\TextColumn::make('slug')
                    ->label('Slug')
                    ->toggleable(),
                Tables\Columns\TextColumn::make('parent.name')
                    ->label('Padre')
                    ->default('—'),
                Tables\Columns\TextColumn::make('products_count')
                    ->label('Prodotti')
                    ->counts('products')
                    ->badge()
                    ->color('info'),
                Tables\Columns\ToggleColumn::make('is_active')
                    ->label('Attiva'),
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
            'index' => Pages\ListCollections::route('/'),
            'create' => Pages\CreateCollection::route('/create'),
            'edit' => Pages\EditCollection::route('/{record}/edit'),
        ];
    }
}
