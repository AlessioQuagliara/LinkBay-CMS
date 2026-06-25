<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources;

use App\Filament\Agency\Concerns\ResolvesCurrentAgency;
use App\Filament\Agency\Resources\LayoutTemplateResource\Pages;
use App\Filament\Agency\Resources\LayoutTemplateResource\RelationManagers;
use App\Models\Central\LayoutTemplate;
use App\Services\FeatureAccessService;
use App\Services\LayoutBlockSchema;
use App\Services\PremiumPackConfig;
use Filament\Forms;
use Filament\Forms\Components\Builder;
use Filament\Notifications\Notification;
use Filament\Resources\Resource;
use Filament\Schemas\Components\Section;
use Filament\Schemas\Schema;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder as EloquentBuilder;
use Illuminate\Support\HtmlString;
use Illuminate\Support\Str;

class LayoutTemplateResource extends Resource
{
    use ResolvesCurrentAgency;

    protected static ?string $model = LayoutTemplate::class;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-rectangle-stack';

    protected static ?string $modelLabel = 'Template';

    protected static ?string $pluralModelLabel = 'Layout Manager';

    protected static ?int $navigationSort = 5;

    // ── Security: scope every query to the current agency ────────────────────

    public static function getEloquentQuery(): EloquentBuilder
    {
        $agency = app()->has('current_agency') ? app('current_agency') : null;

        return parent::getEloquentQuery()
            ->when(
                $agency,
                fn (EloquentBuilder $q) => $q->where('agency_id', $agency->id),
                fn (EloquentBuilder $q) => $q->whereRaw('1=0'),
            );
    }

    // ── Form ─────────────────────────────────────────────────────────────────

    public static function form(Schema $schema): Schema
    {
        return $schema->schema([
            Section::make('Informazioni template')
                ->schema([
                    Forms\Components\TextInput::make('name')
                        ->label('Nome template')
                        ->required()
                        ->maxLength(255)
                        ->live(onBlur: true)
                        ->afterStateUpdated(function (Forms\Set $set, ?string $state, $record) {
                            // Auto-fill slug only on create (no record yet).
                            if ($record === null && $state) {
                                $set('slug', Str::slug($state));
                            }
                        }),
                    Forms\Components\TextInput::make('slug')
                        ->label('Slug')
                        ->required()
                        ->maxLength(255)
                        ->unique(LayoutTemplate::class, 'slug', ignoreRecord: true, modifyRuleUsing: function ($rule) {
                            $agency = app()->has('current_agency') ? app('current_agency') : null;

                            return $agency ? $rule->where('agency_id', $agency->id) : $rule;
                        })
                        ->helperText('Identificatore URL-safe, unico per la tua agency.'),
                    Forms\Components\Select::make('status')
                        ->label('Stato')
                        ->options([
                            LayoutTemplate::STATUS_DRAFT => 'Bozza',
                            LayoutTemplate::STATUS_PUBLISHED => 'Pubblicato',
                        ])
                        ->default(LayoutTemplate::STATUS_DRAFT)
                        ->required(),
                ])
                ->columns(3),

            Section::make('Marketing Block Pack non incluso')
                ->icon('heroicon-o-lock-closed')
                ->iconColor('warning')
                ->description('Questo account non ha accesso al Marketing Block Pack. Il Builder mostra solo i blocchi gratuiti.')
                ->schema([
                    Forms\Components\Placeholder::make('block_pack_nudge')
                        ->label('')
                        ->content(function (): HtmlString {
                            $pack = PremiumPackConfig::forCode('block_pack_marketing');
                            $items = implode(', ', $pack['includes'] ?? []);
                            $entitlementsUrl = route('filament.agency.pages.my-entitlements');
                            $supportEmail = config('mail.from.address', 'support@linkbay.it');

                            return new HtmlString(
                                '<p class="text-sm text-gray-600 dark:text-gray-400">Blocchi inclusi nel pack: <span class="font-medium">'.e($items).'</span>.</p>'.
                                '<div class="mt-3 flex flex-wrap items-center gap-4">'.
                                '<a href="'.e($entitlementsUrl).'" class="text-sm font-semibold text-primary-600 hover:text-primary-500 dark:text-primary-400 dark:hover:text-primary-300 transition-colors">Vedi i miei entitlement →</a>'.
                                '<span class="text-gray-300 dark:text-gray-600 select-none">·</span>'.
                                '<a href="mailto:'.e($supportEmail).'" class="text-sm font-medium text-gray-600 hover:text-gray-500 dark:text-gray-400 transition-colors">Richiedi attivazione</a>'.
                                '</div>'
                            );
                        })
                        ->columnSpanFull(),
                ])
                ->visible(function (): bool {
                    $agency = app()->has('current_agency') ? app('current_agency') : null;
                    if (! $agency) {
                        return false;
                    }

                    return ! app(FeatureAccessService::class)->canUseFeature($agency, 'block_pack_marketing');
                }),

            Section::make('Blocchi contenuto')
                ->description('Componi la pagina aggiungendo e ordinando i blocchi. Le modifiche vengono salvate con il pulsante "Salva".')
                ->schema([
                    Builder::make('blocks')
                        ->label('')
                        ->blocks(LayoutBlockSchema::blocksForAgency(
                            app()->has('current_agency') ? app('current_agency') : null
                        ))
                        ->addActionLabel('Aggiungi blocco')
                        ->collapsible()
                        ->cloneable()
                        ->reorderableWithButtons()
                        ->columnSpanFull(),
                ]),
        ]);
    }

    // ── Table ────────────────────────────────────────────────────────────────

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('name')
                    ->label('Nome')
                    ->searchable()
                    ->sortable()
                    ->weight('medium'),
                Tables\Columns\TextColumn::make('slug')
                    ->label('Slug')
                    ->searchable()
                    ->fontFamily('mono')
                    ->color('gray'),
                Tables\Columns\BadgeColumn::make('status')
                    ->label('Stato')
                    ->formatStateUsing(fn (string $state) => match ($state) {
                        LayoutTemplate::STATUS_PUBLISHED => 'Pubblicato',
                        default => 'Bozza',
                    })
                    ->colors([
                        'success' => LayoutTemplate::STATUS_PUBLISHED,
                        'gray' => LayoutTemplate::STATUS_DRAFT,
                    ]),
                Tables\Columns\TextColumn::make('assignments_count')
                    ->label('Store')
                    ->counts('assignments')
                    ->badge()
                    ->color('primary'),
                Tables\Columns\TextColumn::make('updated_at')
                    ->label('Modificato')
                    ->dateTime('d/m/Y H:i')
                    ->sortable(),
            ])
            ->defaultSort('updated_at', 'desc')
            ->filters([
                Tables\Filters\SelectFilter::make('status')
                    ->options([
                        LayoutTemplate::STATUS_DRAFT => 'Bozza',
                        LayoutTemplate::STATUS_PUBLISHED => 'Pubblicato',
                    ]),
            ])
            ->actions([
                Tables\Actions\EditAction::make()->label('Modifica'),

                Tables\Actions\Action::make('publish')
                    ->label('Pubblica')
                    ->icon('heroicon-o-eye')
                    ->color('success')
                    ->visible(fn (LayoutTemplate $record) => $record->isDraft())
                    ->requiresConfirmation()
                    ->modalHeading('Pubblica template')
                    ->modalDescription('Il template sarà visibile agli store assegnati.')
                    ->action(function (LayoutTemplate $record): void {
                        $record->publish();
                        Notification::make()->title('Template pubblicato')->success()->send();
                    }),

                Tables\Actions\Action::make('unpublish')
                    ->label('Bozza')
                    ->icon('heroicon-o-eye-slash')
                    ->color('warning')
                    ->visible(fn (LayoutTemplate $record) => $record->isPublished())
                    ->requiresConfirmation()
                    ->modalHeading('Rimetti in bozza')
                    ->modalDescription('Il template non sarà più visibile agli store assegnati.')
                    ->action(function (LayoutTemplate $record): void {
                        $record->unpublish();
                        Notification::make()->title('Template rimesso in bozza')->warning()->send();
                    }),

                Tables\Actions\Action::make('duplicate')
                    ->label('Duplica')
                    ->icon('heroicon-o-document-duplicate')
                    ->color('gray')
                    ->form([
                        Forms\Components\TextInput::make('new_name')
                            ->label('Nome del nuovo template')
                            ->required()
                            ->maxLength(255),
                    ])
                    ->action(function (LayoutTemplate $record, array $data): void {
                        $copy = $record->duplicate($data['new_name']);
                        Notification::make()
                            ->title("Template duplicato: {$copy->name}")
                            ->success()
                            ->send();
                    }),

                Tables\Actions\DeleteAction::make(),
            ])
            ->emptyStateHeading('Nessun template')
            ->emptyStateDescription('Crea il primo layout template per comporre le pagine dei tuoi store.')
            ->emptyStateIcon('heroicon-o-rectangle-stack');
    }

    // ── Relations ────────────────────────────────────────────────────────────

    public static function getRelations(): array
    {
        return [
            RelationManagers\AssignmentsRelationManager::class,
        ];
    }

    // ── Pages ────────────────────────────────────────────────────────────────

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListLayoutTemplates::route('/'),
            'create' => Pages\CreateLayoutTemplate::route('/create'),
            'edit' => Pages\EditLayoutTemplate::route('/{record}/edit'),
        ];
    }
}
