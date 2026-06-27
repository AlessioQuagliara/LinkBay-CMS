<?php

namespace App\Filament\Tenant\Resources;

use App\Filament\Tenant\Resources\CategoryResource\Pages;
use App\Models\Tenant\Category;
use Filament\Actions\BulkActionGroup;
use Filament\Actions\DeleteAction;
use Filament\Actions\DeleteBulkAction;
use Filament\Actions\EditAction;
use Filament\Forms;
use Filament\Resources\Resource;
use Filament\Schemas\Components\Section;
use Filament\Schemas\Components\Utilities\Set;
use Filament\Schemas\Schema;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Support\Str;

class CategoryResource extends Resource
{
    protected static ?string $model = Category::class;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-tag';

    protected static string|\UnitEnum|null $navigationGroup = 'Catalogo';

    protected static ?string $modelLabel = 'Categoria';

    protected static ?string $pluralModelLabel = 'Categorie';

    protected static ?int $navigationSort = 2;

    public static function form(Schema $schema): Schema
    {
        return $schema->schema([
            Section::make('Informazioni categoria')
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
                        ->unique(Category::class, 'slug', ignoreRecord: true)
                        ->maxLength(255),
                    Forms\Components\Textarea::make('description')
                        ->label('Descrizione')
                        ->rows(3)
                        ->columnSpanFull(),
                    Forms\Components\Select::make('parent_id')
                        ->label('Categoria padre')
                        ->relationship('parent', 'name')
                        ->searchable()
                        ->preload()
                        ->placeholder('Nessuna (categoria principale)')
                        ->nullable(),
                    Forms\Components\TextInput::make('image_url')
                        ->label('URL immagine')
                        ->url()
                        ->maxLength(2048),
                    Forms\Components\TextInput::make('sort_order')
                        ->label('Ordine')
                        ->integer()
                        ->default(0),
                    Forms\Components\Toggle::make('is_active')
                        ->label('Attiva')
                        ->default(true),
                ])->columns(2),
        ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\ImageColumn::make('image_url')
                    ->label('')
                    ->size(40)
                    ->defaultImageUrl(fn () => 'https://via.placeholder.com/40'),
                Tables\Columns\TextColumn::make('name')
                    ->label('Nome')
                    ->searchable()
                    ->sortable(),
                Tables\Columns\TextColumn::make('slug')
                    ->label('Slug')
                    ->toggleable(isToggledHiddenByDefault: true),
                Tables\Columns\TextColumn::make('parent.name')
                    ->label('Padre')
                    ->placeholder('—')
                    ->toggleable(),
                Tables\Columns\TextColumn::make('products_count')
                    ->label('Prodotti')
                    ->counts('products')
                    ->sortable(),
                Tables\Columns\TextColumn::make('sort_order')
                    ->label('Ordine')
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
                Tables\Columns\ToggleColumn::make('is_active')
                    ->label('Attiva'),
                Tables\Columns\TextColumn::make('created_at')
                    ->label('Creata')
                    ->date('d/m/Y')
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
            ])
            ->filters([
                Tables\Filters\TernaryFilter::make('is_active')->label('Solo attive'),
                Tables\Filters\SelectFilter::make('parent_id')
                    ->label('Categoria padre')
                    ->relationship('parent', 'name')
                    ->placeholder('Tutte'),
            ])
            ->actions([
                EditAction::make(),
                DeleteAction::make(),
            ])
            ->bulkActions([
                BulkActionGroup::make([
                    DeleteBulkAction::make(),
                ]),
            ])
            ->defaultSort('sort_order');
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListCategories::route('/'),
            'create' => Pages\CreateCategory::route('/create'),
            'edit' => Pages\EditCategory::route('/{record}/edit'),
        ];
    }
}
