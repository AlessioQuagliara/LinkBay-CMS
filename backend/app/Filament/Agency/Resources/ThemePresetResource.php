<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources;

use App\Filament\Agency\Concerns\ResolvesCurrentAgency;
use App\Filament\Agency\Resources\ThemePresetResource\Pages;
use App\Filament\Agency\Resources\ThemePresetResource\RelationManagers;
use App\Models\Central\ThemePreset;
use App\Services\ThemeConfigSchema;
use Filament\Forms;
use Filament\Notifications\Notification;
use Filament\Resources\Resource;
use Filament\Schemas\Components\Section;
use Filament\Schemas\Schema;
use Filament\Tables;
use Filament\Tables\Table;
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

    // ── Security: show system presets + agency's own presets ──────────────────

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

    // ── Form ─────────────────────────────────────────────────────────────────

    public static function form(Schema $schema): Schema
    {
        return $schema->schema([
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
                        ->required(),
                    Forms\Components\Select::make('cfg_header_style')
                        ->label('Stile header')
                        ->options(ThemeConfigSchema::HEADER_STYLES)
                        ->required(),
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
                    ->getStateUsing(fn (ThemePreset $record) => $record->is_system ? 'system' : 'agency')
                    ->formatStateUsing(fn (string $state) => $state === 'system' ? 'Sistema' : 'Agenzia')
                    ->colors([
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

                Tables\Actions\Action::make('duplicate')
                    ->label('Duplica')
                    ->icon('heroicon-o-document-duplicate')
                    ->color('gray')
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
