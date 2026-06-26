<?php

namespace App\Filament\Tenant\Resources;

use App\Filament\Tenant\Resources\StorePageResource\Pages;
use App\Models\Tenant\Page;
use App\Services\LayoutBlockSchema;
use Filament\Actions\BulkActionGroup;
use Filament\Actions\DeleteAction;
use Filament\Actions\DeleteBulkAction;
use Filament\Actions\EditAction;
use Filament\Forms;
use Filament\Forms\Components\Builder;
use Filament\Resources\Resource;
use Filament\Schemas\Components\Section;
use Filament\Schemas\Components\Utilities\Set;
use Filament\Schemas\Schema;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Support\Str;

class StorePageResource extends Resource
{
    protected static ?string $model = Page::class;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-document-text';

    protected static string|\UnitEnum|null $navigationGroup = 'Marketing';

    protected static ?string $modelLabel = 'Pagina';

    protected static ?string $pluralModelLabel = 'Pagine';

    protected static ?int $navigationSort = 5;

    public static function form(Schema $schema): Schema
    {
        $agency = null;
        try {
            if (function_exists('tenancy') && tenancy()->initialized) {
                $agency = tenant()?->agency;
            }
        } catch (\Throwable) {
        }

        return $schema->schema([
            Section::make('Contenuto')
                ->schema([
                    Forms\Components\TextInput::make('title')
                        ->label('Titolo')
                        ->required()
                        ->maxLength(255)
                        ->live(onBlur: true)
                        ->afterStateUpdated(fn ($state, Set $set) => $set('slug', Str::slug($state))
                        ),
                    Forms\Components\TextInput::make('slug')
                        ->label('Slug')
                        ->required()
                        ->unique(Page::class, 'slug', ignoreRecord: true)
                        ->maxLength(255),
                    Forms\Components\Toggle::make('is_published')
                        ->label('Pubblicata')
                        ->default(true),
                    Forms\Components\TextInput::make('sort_order')
                        ->label('Ordinamento')
                        ->numeric()
                        ->default(0),
                ])->columns(2),

            Section::make('Blocchi')
                ->description('Componi la pagina aggiungendo e ordinando i blocchi.')
                ->schema([
                    Builder::make('content')
                        ->label('')
                        ->blocks(LayoutBlockSchema::blocksForAgency($agency))
                        ->addActionLabel('Aggiungi blocco')
                        ->collapsible()
                        ->cloneable()
                        ->reorderableWithButtons()
                        ->columnSpanFull(),
                ]),

            Section::make('SEO')
                ->collapsed()
                ->schema([
                    Forms\Components\TextInput::make('meta_title')
                        ->label('Meta Title')
                        ->maxLength(255),
                    Forms\Components\Textarea::make('meta_description')
                        ->label('Meta Description')
                        ->maxLength(500)
                        ->rows(3),
                ])->columns(2),
        ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('title')
                    ->label('Titolo')
                    ->searchable()
                    ->sortable()
                    ->weight('medium'),
                Tables\Columns\TextColumn::make('slug')
                    ->label('Slug')
                    ->searchable()
                    ->fontFamily('mono')
                    ->color('gray'),
                Tables\Columns\IconColumn::make('is_published')
                    ->label('Pubbl.')
                    ->boolean(),
                Tables\Columns\TextColumn::make('sort_order')
                    ->label('Ord.')
                    ->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
                Tables\Columns\TextColumn::make('updated_at')
                    ->label('Modificata')
                    ->dateTime('d/m/Y H:i')
                    ->sortable(),
            ])
            ->defaultSort('sort_order')
            ->actions([
                EditAction::make(),
                DeleteAction::make(),
            ])
            ->bulkActions([
                BulkActionGroup::make([
                    DeleteBulkAction::make(),
                ]),
            ])
            ->emptyStateHeading('Nessuna pagina')
            ->emptyStateDescription('Crea la prima pagina del tuo store.')
            ->emptyStateIcon('heroicon-o-document-text');
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListStorePages::route('/'),
            'create' => Pages\CreateStorePage::route('/create'),
            'edit' => Pages\EditStorePage::route('/{record}/edit'),
        ];
    }
}
