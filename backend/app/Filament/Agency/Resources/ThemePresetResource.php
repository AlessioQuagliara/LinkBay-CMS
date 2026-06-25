<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources;

use App\Filament\Agency\Concerns\ResolvesCurrentAgency;
use App\Filament\Agency\Resources\ThemePresetResource\Pages;
use App\Filament\Agency\Resources\ThemePresetResource\RelationManagers;
use App\Models\Central\ThemePreset;
use App\Models\Central\UsageEvent;
use App\Plugins\PluginRegistry;
use App\Services\FeatureAccessService;
use App\Services\ThemeConfigSchema;
use App\Services\ThemeForkResolver;
use App\Services\UsageEventService;
use Filament\Forms;
use Filament\Notifications\Actions\Action;
use Filament\Notifications\Notification;
use Filament\Resources\Resource;
use Filament\Schemas\Components\Section;
use Filament\Schemas\Schema;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Contracts\View\View;
use Illuminate\Database\Eloquent\Builder as EloquentBuilder;
use Illuminate\Support\Str;

class ThemePresetResource extends Resource
{
    use ResolvesCurrentAgency;

    protected static ?string $model = ThemePreset::class;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-swatch';

    protected static ?string $modelLabel = 'Tema';

    protected static ?string $pluralModelLabel = 'Temi';

    protected static ?int $navigationSort = 6;

    // ── Security: show all system presets + agency's own presets ─────────────
    // Premium system presets (featureCode != null) are shown to everyone, but
    // marked as "Preview" when the agency has no entitlement. Access is enforced
    // per-action (preview only) and by LayoutRendererService on the storefront.

    public static function getEloquentQuery(): EloquentBuilder
    {
        $agency = app()->has('current_agency') ? app('current_agency') : null;

        return parent::getEloquentQuery()
            ->when(
                $agency,
                fn (EloquentBuilder $q) => $q->visibleTo($agency->id),
                fn (EloquentBuilder $q) => $q->whereRaw('1=0'),
            );
    }

    /**
     * Returns true when this system preset can be forked by the current agency.
     * Forks are only allowed on system themes (not on agency presets or existing forks),
     * and only when the agency has access (premium presets in preview mode cannot be forked).
     */
    private static function canForkRecord(ThemePreset $record): bool
    {
        return $record->is_system && ! static::isPremiumPreview($record);
    }

    /**
     * Returns true when this is a premium system preset the current agency
     * cannot use yet — i.e., it should be shown in "Preview" mode only.
     */
    public static function isPremiumPreview(ThemePreset $record): bool
    {
        if (! $record->is_system) {
            return false;
        }

        $def = app(PluginRegistry::class)->getTheme($record->slug);

        if ($def?->featureCode === null) {
            return false;
        }

        $agency = app()->has('current_agency') ? app('current_agency') : null;

        if (! $agency) {
            return true;
        }

        return ! app(FeatureAccessService::class)->canUseFeature($agency, $def->featureCode);
    }

    // ── Form ─────────────────────────────────────────────────────────────────

    public static function form(Schema $schema): Schema
    {
        return $schema->schema([
            // Fork info banner — visible only when editing an inherited variant
            Section::make('Variante derivata da tema base')
                ->description(fn ($record) => $record?->isFork()
                    ? 'Questa variante eredita la struttura del tema '.
                      (app(PluginRegistry::class)->getTheme($record->parent_theme_slug)?->label ?? $record->parent_theme_slug).
                      '. Colori, tipografia, bordi, spaziatura e pulsanti sono personalizzabili. '.
                      'Stile sezione e header sono ereditati e non modificabili — cambieranno automaticamente se il tema base viene aggiornato.'
                    : '')
                ->icon('heroicon-o-link')
                ->iconColor('indigo')
                ->schema([
                    Forms\Components\Placeholder::make('fork_parent_label')
                        ->label('Tema base')
                        ->content(fn ($record): string => $record?->isFork()
                            ? (app(PluginRegistry::class)->getTheme($record->parent_theme_slug)?->label ?? ($record->parent_theme_slug ?? '—'))
                            : '—'),
                ])
                ->visible(fn ($record) => (bool) $record?->isFork()),

            Section::make('Informazioni tema')
                ->schema([
                    Forms\Components\TextInput::make('name')
                        ->label('Nome tema')
                        ->required()
                        ->maxLength(255)
                        ->live(onBlur: true)
                        ->afterStateUpdated(function (Forms\Set $set, ?string $state, $record) {
                            if ($record === null && $state) {
                                $set('slug', Str::slug($state));
                            }
                        }),
                    Forms\Components\TextInput::make('slug')
                        ->label('Slug')
                        ->required()
                        ->maxLength(255)
                        ->unique(ThemePreset::class, 'slug', ignoreRecord: true, modifyRuleUsing: function ($rule) {
                            $agency = app()->has('current_agency') ? app('current_agency') : null;

                            return $agency ? $rule->where('agency_id', $agency->id) : $rule;
                        })
                        ->helperText('Identificatore URL-safe, unico per la tua agency.'),
                    Forms\Components\Select::make('status')
                        ->label('Stato')
                        ->options([
                            ThemePreset::STATUS_DRAFT => 'Bozza',
                            ThemePreset::STATUS_ACTIVE => 'Attivo',
                        ])
                        ->default(ThemePreset::STATUS_DRAFT)
                        ->required(),
                ])
                ->columns(3),

            Section::make('Palette colori')
                ->description('Colori nel formato esadecimale #rrggbb.')
                ->schema([
                    Forms\Components\ColorPicker::make('cfg_palette_primary')->label('Primario')->required(),
                    Forms\Components\ColorPicker::make('cfg_palette_secondary')->label('Secondario')->required(),
                    Forms\Components\ColorPicker::make('cfg_palette_accent')->label('Accento')->required(),
                    Forms\Components\ColorPicker::make('cfg_palette_surface')->label('Sfondo')->required(),
                    Forms\Components\ColorPicker::make('cfg_palette_text')->label('Testo')->required(),
                ])
                ->columns(5),

            Section::make('Tipografia')
                ->schema([
                    Forms\Components\Select::make('cfg_typography_heading_font')
                        ->label('Font titoli')
                        ->options(ThemeConfigSchema::HEADING_FONTS)
                        ->required(),
                    Forms\Components\Select::make('cfg_typography_body_font')
                        ->label('Font corpo')
                        ->options(ThemeConfigSchema::BODY_FONTS)
                        ->required(),
                    Forms\Components\Select::make('cfg_typography_scale')
                        ->label('Scala tipografica')
                        ->options(ThemeConfigSchema::SCALE_OPTIONS)
                        ->required(),
                ])
                ->columns(3),

            Section::make('Stile interfaccia')
                ->schema([
                    Forms\Components\Select::make('cfg_radius')
                        ->label('Arrotondamento')
                        ->options(ThemeConfigSchema::RADIUS_OPTIONS)
                        ->required(),
                    Forms\Components\Select::make('cfg_spacing')
                        ->label('Spaziatura')
                        ->options(ThemeConfigSchema::SPACING_OPTIONS)
                        ->required(),
                    Forms\Components\Select::make('cfg_buttons')
                        ->label('Stile pulsanti')
                        ->options(ThemeConfigSchema::BUTTON_OPTIONS)
                        ->required(),
                    Forms\Components\Select::make('cfg_section_style')
                        ->label('Stile sezione')
                        ->options(ThemeConfigSchema::SECTION_STYLES)
                        ->required()
                        ->disabled(fn ($record) => (bool) $record?->isFork())
                        ->helperText(fn ($record) => $record?->isFork() ? 'Ereditato dal tema base — non personalizzabile.' : null),
                    Forms\Components\Select::make('cfg_header_style')
                        ->label('Stile header')
                        ->options(ThemeConfigSchema::HEADER_STYLES)
                        ->required()
                        ->disabled(fn ($record) => (bool) $record?->isFork())
                        ->helperText(fn ($record) => $record?->isFork() ? 'Ereditato dal tema base — non personalizzabile.' : null),
                ])
                ->columns(5),
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
                        ThemePreset::STATUS_ACTIVE => 'Attivo',
                        default => 'Bozza',
                    })
                    ->colors([
                        'success' => ThemePreset::STATUS_ACTIVE,
                        'gray' => ThemePreset::STATUS_DRAFT,
                    ]),
                Tables\Columns\BadgeColumn::make('origin')
                    ->label('Origine')
                    ->getStateUsing(function (ThemePreset $record): string {
                        if (! $record->is_system) {
                            return 'agency';
                        }
                        $def = app(PluginRegistry::class)->getTheme($record->slug);

                        if ($def?->featureCode === null) {
                            return 'system';
                        }

                        return static::isPremiumPreview($record) ? 'preview' : 'premium';
                    })
                    ->formatStateUsing(fn (string $state) => match ($state) {
                        'premium' => 'Premium',
                        'preview' => 'Anteprima',
                        'system' => 'Sistema',
                        default => 'Agenzia',
                    })
                    ->colors([
                        'warning' => 'premium',
                        'info' => 'preview',
                        'primary' => 'system',
                        'gray' => 'agency',
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
            ->defaultSort('is_system', 'desc')
            ->filters([
                Tables\Filters\SelectFilter::make('status')
                    ->options([
                        ThemePreset::STATUS_DRAFT => 'Bozza',
                        ThemePreset::STATUS_ACTIVE => 'Attivo',
                    ]),
                Tables\Filters\TernaryFilter::make('is_system')
                    ->label('Origine')
                    ->trueLabel('Solo sistema')
                    ->falseLabel('Solo agenzia')
                    ->nullable(),
            ])
            ->actions([
                Tables\Actions\EditAction::make()
                    ->label('Modifica')
                    ->visible(fn (ThemePreset $record) => ! $record->is_system),

                Tables\Actions\Action::make('activate')
                    ->label('Attiva')
                    ->icon('heroicon-o-check-circle')
                    ->color('success')
                    ->visible(fn (ThemePreset $record) => ! $record->is_system && $record->isDraft())
                    ->requiresConfirmation()
                    ->action(function (ThemePreset $record): void {
                        $record->activate();
                        Notification::make()->title('Tema attivato')->success()->send();
                    }),

                Tables\Actions\Action::make('deactivate')
                    ->label('Disattiva')
                    ->icon('heroicon-o-x-circle')
                    ->color('warning')
                    ->visible(fn (ThemePreset $record) => ! $record->is_system && $record->isActive())
                    ->requiresConfirmation()
                    ->action(function (ThemePreset $record): void {
                        $record->deactivate();
                        Notification::make()->title('Tema disattivato')->warning()->send();
                    }),

                Tables\Actions\Action::make('preview')
                    ->label('Anteprima')
                    ->icon('heroicon-o-eye')
                    ->color('gray')
                    ->visible(fn (ThemePreset $record): bool => static::isPremiumPreview($record))
                    ->modalHeading(fn (ThemePreset $record): string => $record->name.' — Anteprima')
                    ->modalContent(function (ThemePreset $record): View {
                        app(UsageEventService::class)->track(
                            eventType: UsageEvent::EVENT_THEME_PREVIEW_OPENED,
                            subjectType: 'theme_preset',
                            subjectId: $record->id,
                            meta: ['theme_slug' => $record->slug],
                        );

                        return view('filament.agency.modals.theme-preview', [
                            'preset' => $record,
                            'definition' => app(PluginRegistry::class)->getTheme($record->slug),
                        ]);
                    })
                    ->modalSubmitAction(false)
                    ->modalCancelActionLabel('Chiudi'),

                Tables\Actions\Action::make('duplicate')
                    ->label('Duplica')
                    ->icon('heroicon-o-document-duplicate')
                    ->color('gray')
                    ->visible(fn (ThemePreset $record): bool => ! static::isPremiumPreview($record))
                    ->form([
                        Forms\Components\TextInput::make('new_name')
                            ->label('Nome del nuovo tema')
                            ->required()
                            ->maxLength(255),
                    ])
                    ->action(function (ThemePreset $record, array $data): void {
                        $agency = app()->has('current_agency') ? app('current_agency') : null;
                        if (! $agency) {
                            Notification::make()->title('Agenzia non trovata')->danger()->send();

                            return;
                        }
                        $copy = $record->duplicate($agency->id, $data['new_name']);
                        Notification::make()
                            ->title("Tema duplicato: {$copy->name}")
                            ->success()
                            ->send();
                    }),

                Tables\Actions\Action::make('fork')
                    ->label('Crea variante')
                    ->icon('heroicon-o-scissors')
                    ->color('indigo')
                    ->visible(fn (ThemePreset $record): bool => static::canForkRecord($record))
                    ->modalHeading(fn (ThemePreset $record): string => 'Crea variante di "'.$record->name.'"')
                    ->modalDescription('La variante eredita palette, tipografia e stile dal tema base. Potrai personalizzare colori, font e spaziatura mantenendo il collegamento con il tema di origine.')
                    ->modalSubmitActionLabel('Crea variante')
                    ->form([
                        Forms\Components\TextInput::make('fork_name')
                            ->label('Nome della variante')
                            ->required()
                            ->maxLength(255)
                            ->placeholder('Es. Meridian / Cliente ACME')
                            ->helperText('Scegli un nome che identifichi chiaramente la personalizzazione rispetto al tema base.'),
                    ])
                    ->action(function (ThemePreset $record, array $data): void {
                        $agency = app()->has('current_agency') ? app('current_agency') : null;

                        if (! $agency) {
                            Notification::make()->title('Agenzia non trovata')->danger()->send();

                            return;
                        }

                        if (! ThemeForkResolver::canFork($agency, $record->slug)) {
                            Notification::make()->title('Accesso non consentito per questo tema.')->danger()->send();

                            return;
                        }

                        $fork = $record->fork($agency->id, $data['fork_name']);

                        app(UsageEventService::class)->track(
                            eventType: UsageEvent::EVENT_THEME_FORK_CREATED,
                            agencyId: $agency->id,
                            subjectType: 'theme_preset',
                            subjectId: $fork->id,
                            meta: ['parent_theme_slug' => $record->slug, 'fork_slug' => $fork->slug],
                        );

                        Notification::make()
                            ->title("Variante \"{$fork->name}\" creata")
                            ->body('Personalizza colori, tipografia e stile della variante.')
                            ->success()
                            ->actions([
                                Action::make('edit_fork')
                                    ->label('Vai alla variante')
                                    ->url(static::getUrl('edit', ['record' => $fork]))
                                    ->button(),
                            ])
                            ->send();
                    }),

                Tables\Actions\DeleteAction::make()
                    ->visible(fn (ThemePreset $record) => ! $record->is_system),
            ])
            ->emptyStateHeading('Nessun tema')
            ->emptyStateDescription('Crea il primo tema o duplica un preset di sistema.')
            ->emptyStateIcon('heroicon-o-swatch');
    }

    // ── Relations ────────────────────────────────────────────────────────────

    public static function getRelations(): array
    {
        return [
            RelationManagers\ThemeAssignmentsRelationManager::class,
        ];
    }

    // ── Pages ────────────────────────────────────────────────────────────────

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListThemePresets::route('/'),
            'create' => Pages\CreateThemePreset::route('/create'),
            'edit' => Pages\EditThemePreset::route('/{record}/edit'),
        ];
    }
}
