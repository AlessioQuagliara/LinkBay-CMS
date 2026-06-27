<?php

namespace App\Filament\Tenant\Resources;

use App\Filament\Tenant\Resources\ProductResource\Pages;
use App\Models\Tenant\Product;
use Filament\Actions\Action;
use Filament\Actions\BulkActionGroup;
use Filament\Actions\DeleteAction;
use Filament\Actions\DeleteBulkAction;
use Filament\Actions\EditAction;
use Filament\Actions\ExportBulkAction;
use Filament\Forms;
use Filament\Infolists;
use Filament\Resources\Resource;
use Filament\Schemas\Components\Section;
use Filament\Schemas\Components\Tabs;
use Filament\Schemas\Components\Utilities\Set;
use Filament\Schemas\Schema;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Support\Str;

class ProductResource extends Resource
{
    protected static ?string $model = Product::class;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-shopping-bag';

    protected static string|\UnitEnum|null $navigationGroup = 'Catalogo';

    protected static ?string $modelLabel = 'Prodotto';

    protected static ?string $pluralModelLabel = 'Prodotti';

    protected static ?int $navigationSort = 1;

    public static function getNavigationBadge(): ?string
    {
        $count = static::getModel()::where('stock', '<=', 5)->where('is_active', true)->count();

        return $count > 0 ? (string) $count : null;
    }

    public static function getNavigationBadgeColor(): string|array|null
    {
        $count = static::getModel()::where('stock', 0)->count();

        return $count > 0 ? 'danger' : 'warning';
    }

    public static function getNavigationBadgeTooltip(): ?string
    {
        return 'Prodotti con stock ≤ 5';
    }

    public static function form(Schema $schema): Schema
    {
        return $schema->schema([
            Section::make('Informazioni base')
                ->schema([
                    Forms\Components\TextInput::make('name')
                        ->label('Nome')
                        ->required()
                        ->maxLength(255)
                        ->live(onBlur: true)
                        ->afterStateUpdated(fn ($state, Set $set) => $set('slug', Str::slug($state))
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

            Section::make('Organizzazione')
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
                                ->afterStateUpdated(fn ($state, Set $set) => $set('slug', Str::slug($state))
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

            Tabs::make('Dettagli avanzati')
                ->tabs([
                    Tabs\Tab::make('Inventario')
                        ->icon('heroicon-o-cube')
                        ->schema([
                            Forms\Components\TextInput::make('barcode')
                                ->label('Codice a barre (EAN/UPC)')
                                ->maxLength(64),
                            Forms\Components\TextInput::make('quantity')
                                ->label('Quantità disponibile')
                                ->numeric()
                                ->default(0),
                            Forms\Components\Toggle::make('track_quantity')
                                ->label('Traccia la quantità')
                                ->default(true),
                            Forms\Components\TextInput::make('cost_per_item')
                                ->label('Costo per articolo (€)')
                                ->numeric()
                                ->prefix('€'),
                            Forms\Components\TextInput::make('compare_at_price')
                                ->label('Prezzo confronto (€)')
                                ->numeric()
                                ->prefix('€'),
                            Forms\Components\Select::make('weight_unit')
                                ->label('Unità peso')
                                ->options(['kg' => 'kg', 'g' => 'g', 'lb' => 'lb', 'oz' => 'oz'])
                                ->default('kg'),
                            Forms\Components\Toggle::make('requires_shipping')
                                ->label('Richiede spedizione')
                                ->default(true),
                            Forms\Components\Toggle::make('is_taxable')
                                ->label('Soggetto a IVA')
                                ->default(true),
                            Forms\Components\TextInput::make('tax_class')
                                ->label('Classe fiscale')
                                ->maxLength(64),
                        ])->columns(2),

                    Tabs\Tab::make('Media')
                        ->icon('heroicon-o-photo')
                        ->schema([
                            Forms\Components\Repeater::make('productImages')
                                ->label('Immagini prodotto')
                                ->relationship()
                                ->schema([
                                    Forms\Components\TextInput::make('url')
                                        ->label('URL immagine')
                                        ->url()
                                        ->required()
                                        ->columnSpan(2),
                                    Forms\Components\TextInput::make('alt_text')
                                        ->label('Testo alternativo'),
                                    Forms\Components\TextInput::make('sort_order')
                                        ->label('Ordine')
                                        ->integer()
                                        ->default(0),
                                    Forms\Components\Toggle::make('is_primary')
                                        ->label('Principale'),
                                ])
                                ->maxItems(20)
                                ->columns(4)
                                ->orderColumn('sort_order')
                                ->collapsible(),
                        ]),

                    Tabs\Tab::make('SEO')
                        ->icon('heroicon-o-magnifying-glass')
                        ->schema([
                            Forms\Components\TextInput::make('seo_title')
                                ->label('Titolo SEO')
                                ->maxLength(70)
                                ->helperText('Lascia vuoto per usare il nome del prodotto')
                                ->columnSpanFull(),
                            Forms\Components\Textarea::make('seo_description')
                                ->label('Meta descrizione')
                                ->rows(3)
                                ->maxLength(160)
                                ->helperText('Massimo 160 caratteri')
                                ->columnSpanFull(),
                            Forms\Components\TextInput::make('seo_keywords')
                                ->label('Parole chiave (separate da virgola)')
                                ->maxLength(255)
                                ->columnSpanFull(),
                        ])->columns(1),
                ])
                ->columnSpanFull(),

            Section::make('Categorie')
                ->schema([
                    Forms\Components\CheckboxList::make('categories')
                        ->label('')
                        ->relationship('categories', 'name')
                        ->searchable()
                        ->columns(3),
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
                    ->color(fn ($state) => match (true) {
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
                EditAction::make(),
                Action::make('duplicate')
                    ->label('Duplica')
                    ->icon('heroicon-o-document-duplicate')
                    ->action(function (Product $record) {
                        $clone = $record->replicate();
                        $clone->name = $record->name.' — Copia';
                        $clone->slug = Str::slug($clone->name);
                        $clone->sku = $record->sku ? $record->sku.'-COPY' : null;
                        $clone->save();
                    }),
                DeleteAction::make(),
            ])
            ->bulkActions([
                BulkActionGroup::make([
                    DeleteBulkAction::make(),
                    ExportBulkAction::make(),
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
