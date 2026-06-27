<?php

namespace App\Filament\Tenant\Resources;

use App\Filament\Tenant\Resources\StorePageResource\Pages;
use App\Models\Tenant\Page;
use Filament\Actions\BulkActionGroup;
use Filament\Actions\DeleteAction;
use Filament\Actions\DeleteBulkAction;
use Filament\Actions\EditAction;
use Filament\Forms;
use Filament\Forms\Components\Builder;
use Filament\Resources\Resource;
use Filament\Schemas\Components\Section;
use Filament\Schemas\Components\Tabs;
use Filament\Schemas\Components\Tabs\Tab;
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
            Tabs::make('Pagina')
                ->tabs([

                    Tab::make('Contenuto')
                        ->icon('heroicon-o-document-text')
                        ->schema([
                            Section::make()
                                ->schema([
                                    Forms\Components\TextInput::make('title')
                                        ->label('Titolo')
                                        ->required()
                                        ->maxLength(255)
                                        ->live(onBlur: true)
                                        ->afterStateUpdated(fn ($state, Set $set) => $set('slug', Str::slug($state))),
                                    Forms\Components\TextInput::make('slug')
                                        ->label('Slug')
                                        ->required()
                                        ->unique(Page::class, 'slug', ignoreRecord: true)
                                        ->maxLength(255),
                                    Forms\Components\Toggle::make('is_published')
                                        ->label('Pubblicata')
                                        ->default(true),
                                    Forms\Components\Toggle::make('is_homepage')
                                        ->label('Homepage')
                                        ->helperText('Se attivato, questa pagina verrà usata come homepage del sito.')
                                        ->reactive()
                                        ->afterStateUpdated(function (bool $state, Set $set, $record) {
                                            if ($state && $record) {
                                                Page::where('id', '!=', $record->id)->update(['is_homepage' => false]);
                                            }
                                        }),
                                    Forms\Components\Select::make('visibility')
                                        ->label('Visibilità')
                                        ->options([
                                            'public' => 'Pubblica',
                                            'private' => 'Privata',
                                            'password_protected' => 'Protetta da password',
                                        ])
                                        ->default('public')
                                        ->live(),
                                    Forms\Components\TextInput::make('page_password')
                                        ->label('Password pagina')
                                        ->password()
                                        ->visible(fn ($get) => $get('visibility') === 'password_protected'),
                                    Forms\Components\DateTimePicker::make('published_at')
                                        ->label('Data pubblicazione programmata')
                                        ->nullable(),
                                    Forms\Components\TextInput::make('sort_order')
                                        ->label('Ordinamento')
                                        ->numeric()
                                        ->default(0),
                                    Forms\Components\Select::make('template')
                                        ->label('Template')
                                        ->options([
                                            'default' => 'Default',
                                            'full-width' => 'Full width',
                                            'landing' => 'Landing page',
                                            'blank' => 'Blank',
                                        ])
                                        ->nullable(),
                                ])->columns(2),
                        ]),

                    Tab::make('Blocchi (Builder)')
                        ->icon('heroicon-o-squares-2x2')
                        ->schema([
                            Section::make()
                                ->description('Componi la pagina aggiungendo e ordinando i blocchi di contenuto.')
                                ->schema([
                                    Builder::make('blocks')
                                        ->label('')
                                        ->blocks([
                                            Builder\Block::make('hero')
                                                ->label('Hero')
                                                ->icon('heroicon-o-photo')
                                                ->schema([
                                                    Forms\Components\TextInput::make('title')->label('Titolo'),
                                                    Forms\Components\TextInput::make('subtitle')->label('Sottotitolo'),
                                                    Forms\Components\TextInput::make('background_url')->label('URL immagine sfondo')->url(),
                                                    Forms\Components\TextInput::make('cta_text')->label('Testo CTA'),
                                                    Forms\Components\TextInput::make('cta_url')->label('URL CTA')->url(),
                                                    Forms\Components\Toggle::make('visible')->label('Visibile')->default(true),
                                                ]),
                                            Builder\Block::make('text')
                                                ->label('Testo')
                                                ->icon('heroicon-o-bars-3-bottom-left')
                                                ->schema([
                                                    Forms\Components\RichEditor::make('body')->label('Contenuto')->columnSpanFull(),
                                                    Forms\Components\Toggle::make('visible')->label('Visibile')->default(true),
                                                ]),
                                            Builder\Block::make('products')
                                                ->label('Prodotti')
                                                ->icon('heroicon-o-shopping-bag')
                                                ->schema([
                                                    Forms\Components\TextInput::make('title')->label('Titolo sezione'),
                                                    Forms\Components\TextInput::make('collection_slug')->label('Slug collection (opz.)'),
                                                    Forms\Components\TextInput::make('limit')->label('Numero prodotti')->numeric()->default(4),
                                                    Forms\Components\Toggle::make('visible')->label('Visibile')->default(true),
                                                ]),
                                            Builder\Block::make('banner')
                                                ->label('Banner')
                                                ->icon('heroicon-o-megaphone')
                                                ->schema([
                                                    Forms\Components\TextInput::make('text')->label('Testo'),
                                                    Forms\Components\ColorPicker::make('background_color')->label('Colore sfondo')->default('#f5f5f5'),
                                                    Forms\Components\TextInput::make('cta_text')->label('Testo CTA'),
                                                    Forms\Components\TextInput::make('cta_url')->label('URL CTA')->url(),
                                                    Forms\Components\Toggle::make('visible')->label('Visibile')->default(true),
                                                ]),
                                            Builder\Block::make('html')
                                                ->label('HTML personalizzato')
                                                ->icon('heroicon-o-code-bracket')
                                                ->schema([
                                                    Forms\Components\Textarea::make('html')->label('HTML')->rows(8)->fontFamily('mono')->columnSpanFull(),
                                                    Forms\Components\Toggle::make('visible')->label('Visibile')->default(true),
                                                ]),
                                            Builder\Block::make('spacer')
                                                ->label('Spaziatura')
                                                ->icon('heroicon-o-arrows-up-down')
                                                ->schema([
                                                    Forms\Components\TextInput::make('height')->label('Altezza (px)')->numeric()->default(40),
                                                    Forms\Components\Toggle::make('visible')->label('Visibile')->default(true),
                                                ]),
                                        ])
                                        ->addActionLabel('Aggiungi blocco')
                                        ->collapsible()
                                        ->cloneable()
                                        ->reorderableWithButtons()
                                        ->columnSpanFull(),
                                ]),
                        ]),

                    Tab::make('SEO')
                        ->icon('heroicon-o-magnifying-glass')
                        ->schema([
                            Section::make()
                                ->schema([
                                    Forms\Components\TextInput::make('seo_title')
                                        ->label('SEO Title')
                                        ->maxLength(255)
                                        ->helperText('Lascia vuoto per usare il titolo pagina'),
                                    Forms\Components\Textarea::make('seo_description')
                                        ->label('SEO Description')
                                        ->maxLength(500)
                                        ->rows(3),
                                    Forms\Components\TextInput::make('og_image_url')
                                        ->label('OG Image URL')
                                        ->url()
                                        ->helperText('URL immagine per condivisione social (1200×630 consigliata)'),
                                    Forms\Components\TextInput::make('meta_title')
                                        ->label('Meta Title (legacy)')
                                        ->maxLength(255)
                                        ->hidden(),
                                    Forms\Components\Textarea::make('meta_description')
                                        ->label('Meta Description (legacy)')
                                        ->maxLength(500)
                                        ->hidden(),
                                ])->columns(2),
                        ]),

                ])
                ->columnSpanFull(),
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
                Tables\Columns\IconColumn::make('is_homepage')
                    ->label('Home')
                    ->boolean()
                    ->toggleable(isToggledHiddenByDefault: false),
                Tables\Columns\IconColumn::make('is_published')
                    ->label('Pubbl.')
                    ->boolean(),
                Tables\Columns\BadgeColumn::make('visibility')
                    ->label('Visibilità')
                    ->colors([
                        'success' => 'public',
                        'warning' => 'password_protected',
                        'danger' => 'private',
                    ])
                    ->formatStateUsing(fn ($state) => match ($state) {
                        'public' => 'Pubblica',
                        'private' => 'Privata',
                        'password_protected' => 'Con password',
                        default => $state,
                    }),
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
