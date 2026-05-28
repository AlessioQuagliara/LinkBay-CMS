<?php

namespace App\Filament\Tenant\Resources;

use App\Filament\Tenant\Resources\ProductResource\Pages;
use App\Models\Tenant\Collection;
use App\Models\Tenant\Product;
use Filament\Forms;
use Filament\Schemas\Schema;

use Filament\Infolists;

use Filament\Resources\Resource;
use Filament\Support\Colors\Color;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Support\Str;

class ProductResource extends Resource
{
    protected static ?string $model = Product::class;
    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-shopping-bag';
    protected static string|\NITENUM|NULL $NAVIGATIONGROUP = 'Catalogo';
    protected static ?string $modelLabel = 'Prodotto';
    protected static ?string $pluralModelLabel = 'Prodotti';
    protected static ?int $navigationSort = 1;

    public static function form(Schema $schema): Schema
    {
        return $schema->schema([
            Forms\Components\Section::make('Informazioni base')
                ->schema([
                    Forms\Components\TextInput::make('name')
                        ->label('Nome')
                        ->required()
                        ->maxLength(255)
                        ->live(onBlur: true)
                        ->afterStateUpdated(fn ($state, Forms\Set $set) =>
                            $set('slug', Str::slug($state))
                        ),
                    Forms\Components\TextInput::make('slug')
                        ->label('Slug')
                        ->required()
                        ->unique(Product::class, 'slug', ignoreRecord: true)
                        ->maxLength(255),
                    Forms\Components\RichEditor::make('description')
                        ->label('Descrizione')
                        ->columnSpanFull(),
                    Forms\Components\TextInput::make('price')
                        ->label('Prezzo (€)')
                        ->numeric()
                        ->required()
                        ->prefix('€'),
                    Forms\Components\TextInput::make('compare_price')
                        ->label('Prezzo barrato (€)')
                        ->numeric()
                        ->prefix('€'),
                    Forms\Components\TextInput::make('sku')
                        ->label('SKU')
                        ->unique(Product::class, 'sku', ignoreRecord: true),
                    Forms\Components\TextInput::make('stock')
                        ->label('Giacenza')
                        ->numeric()
                        ->default(0)
                        ->required(),
                    Forms\Components\Toggle::make('is_active')
                        ->label('Attivo')
                        ->default(true),
                ])->columns(2),

            Forms\Components\Section::make('Organizzazione')
                ->schema([
                    Forms\Components\Select::make('collection_id')
                        ->label('Collezione')
                        ->relationship('collection', 'name')
                        ->searchable()
                        ->preload()
                        ->createOptionForm([
                            Forms\Components\TextInput::make('name')
                                ->required()
                                ->live(onBlur: true)
                                ->afterStateUpdated(fn ($state, Forms\Set $set) =>
                                    $set('slug', Str::slug($state))
                                ),
                            Forms\Components\TextInput::make('slug')->required(),
                        ]),
                    Forms\Components\TextInput::make('weight')
                        ->label('Peso (kg)')
                        ->numeric()
                        ->suffix('kg'),
                    Forms\Components\KeyValue::make('metadata')
                        ->label('Metadati aggiuntivi'),
                ])->columns(2),

            Forms\Components\Section::make('Immagini')
                ->schema([
                    Forms\Components\Repeater::make('images')
                        ->label('Immagini prodotto')
                        ->schema([
                            Forms\Components\TextInput::make('url')
                                ->label('URL immagine')
                                ->url()
                                ->required(),
                            Forms\Components\TextInput::make('alt')
                                ->label('Testo alternativo'),
                        ])
                        ->maxItems(10)
                        ->columns(2)
                        ->collapsed(),
                ]),
        ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\ImageColumn::make('images.0.url')
                    ->label('')
                    ->size(48)
                    ->defaultImageUrl(fn () => 'https://via.placeholder.com/48'),
                Tables\Columns\TextColumn::make('name')
                    ->label('Nome')
                    ->searchable()
                    ->sortable(),
                Tables\Columns\TextColumn::make('sku')
                    ->label('SKU')
                    ->searchable()
                    ->toggleable(),
                Tables\Columns\TextColumn::make('price')
                    ->label('Prezzo')
                    ->money('EUR')
                    ->sortable(),
                Tables\Columns\TextColumn::make('stock')
                    ->label('Stock')
                    ->badge()
                    ->color(fn ($state) => match(true) {
                        $state <= 0 => 'danger',
                        $state <= 10 => 'warning',
                        default => 'success',
                    })
                    ->sortable(),
                Tables\Columns\TextColumn::make('collection.name')
                    ->label('Collezione')
                    ->toggleable(),
                Tables\Columns\ToggleColumn::make('is_active')
                    ->label('Attivo'),
                Tables\Columns\TextColumn::make('created_at')
                    ->label('Creato')
                    ->date('d/m/Y')
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
            ])
            ->filters([
                Tables\Filters\SelectFilter::make('collection_id')
                    ->label('Collezione')
                    ->relationship('collection', 'name'),
                Tables\Filters\TernaryFilter::make('is_active')
                    ->label('Solo attivi'),
                Tables\Filters\Filter::make('price_range')
                    ->form([
                        Forms\Components\TextInput::make('price_from')->label('Prezzo da')->numeric(),
                        Forms\Components\TextInput::make('price_to')->label('Prezzo a')->numeric(),
                    ])
                    ->query(fn ($query, array $data) => $query
                        ->when($data['price_from'], fn ($q) => $q->where('price', '>=', $data['price_from']))
                        ->when($data['price_to'], fn ($q) => $q->where('price', '<=', $data['price_to']))
                    ),
            ])
            ->actions([
                \Filament\Actions\EditAction::make(),
                \Filament\Actions\Action::make('duplicate')
                    ->label('Duplica')
                    ->icon('heroicon-o-document-duplicate')
                    ->action(function (Product $record) {
                        $clone = $record->replicate();
                        $clone->name = $record->name . ' — Copia';
                        $clone->slug = Str::slug($clone->name);
                        $clone->sku = $record->sku ? $record->sku . '-COPY' : null;
                        $clone->save();
                    }),
                \Filament\Actions\DeleteAction::make(),
            ])
            ->bulkActions([
                \Filament\Actions\BulkActionGroup::make([
                    \Filament\Actions\DeleteBulkAction::make(),
                    \Filament\Actions\ExportBulkAction::make(),
                ]),
            ])
            ->defaultSort('created_at', 'desc');
    }

    public static function infolist(Schema $schema): Schema
    {
        return $schema->schema([
            Infolists\Components\Section::make('Prodotto')
                ->schema([
                    Infolists\Components\ImageEntry::make('images.0.url')
                        ->label('Immagine')
                        ->height(200),
                    Infolists\Components\TextEntry::make('name')->label('Nome'),
                    Infolists\Components\TextEntry::make('slug')->label('Slug'),
                    Infolists\Components\TextEntry::make('description')
                        ->label('Descrizione')
                        ->html()
                        ->columnSpanFull(),
                    Infolists\Components\TextEntry::make('price')
                        ->label('Prezzo')
                        ->money('EUR'),
                    Infolists\Components\TextEntry::make('compare_price')
                        ->label('Prezzo barrato')
                        ->money('EUR'),
                    Infolists\Components\TextEntry::make('sku')->label('SKU'),
                    Infolists\Components\TextEntry::make('stock')->label('Giacenza'),
                    Infolists\Components\TextEntry::make('collection.name')->label('Collezione'),
                    Infolists\Components\IconEntry::make('is_active')
                        ->label('Attivo')
                        ->boolean(),
                ])->columns(2),
        ]);
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListProducts::route('/'),
            'create' => Pages\CreateProduct::route('/create'),
            'edit' => Pages\EditProduct::route('/{record}/edit'),
        ];
    }
}
