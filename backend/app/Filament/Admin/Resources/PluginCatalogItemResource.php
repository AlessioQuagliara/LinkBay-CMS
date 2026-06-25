<?php

declare(strict_types=1);

namespace App\Filament\Admin\Resources;

use App\Filament\Admin\Resources\PluginCatalogItemResource\Pages;
use App\Models\Central\PluginCatalogItem;
use Filament\Forms;
use Filament\Resources\Resource;
use Filament\Schemas\Schema;
use Filament\Tables;
use Filament\Tables\Table;

class PluginCatalogItemResource extends Resource
{
    protected static ?string $model = PluginCatalogItem::class;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-puzzle-piece';

    protected static string|\UnitEnum|null $navigationGroup = 'Marketplace';

    protected static ?string $modelLabel = 'Catalog Item';

    protected static ?string $pluralModelLabel = 'Catalog Items';

    public static function form(Schema $schema): Schema
    {
        return $schema->schema([
            Forms\Components\TextInput::make('code')
                ->label('Codice univoco')
                ->required()
                ->unique(PluginCatalogItem::class, 'code', ignoreRecord: true)
                ->maxLength(100)
                ->helperText('Es: theme_premium, block_pack_pro — non modificabile dopo la creazione.')
                ->alphaDash(),
            Forms\Components\TextInput::make('name')
                ->label('Nome')
                ->required()
                ->maxLength(255),
            Forms\Components\Select::make('type')
                ->label('Tipo')
                ->options(PluginCatalogItem::TYPES)
                ->required(),
            Forms\Components\Select::make('status')
                ->label('Stato')
                ->options(PluginCatalogItem::STATUSES)
                ->default(PluginCatalogItem::STATUS_DRAFT)
                ->required(),
            Forms\Components\Textarea::make('description')
                ->label('Descrizione')
                ->rows(3)
                ->columnSpanFull(),
            Forms\Components\KeyValue::make('config')
                ->label('Config extra (JSON)')
                ->columnSpanFull(),
        ])->columns(2);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\IconColumn::make('is_system')
                    ->label('Sistema')
                    ->boolean()
                    ->trueIcon('heroicon-o-cpu-chip')
                    ->falseIcon('heroicon-o-user')
                    ->trueColor('primary')
                    ->falseColor('gray'),
                Tables\Columns\TextColumn::make('code')
                    ->label('Codice')
                    ->searchable()
                    ->fontFamily('mono')
                    ->copyable(),
                Tables\Columns\TextColumn::make('name')
                    ->label('Nome')
                    ->searchable()
                    ->sortable(),
                Tables\Columns\BadgeColumn::make('type')
                    ->label('Tipo')
                    ->formatStateUsing(fn (string $state) => PluginCatalogItem::TYPES[$state] ?? $state)
                    ->colors([
                        'info' => PluginCatalogItem::TYPE_FEATURE,
                        'primary' => PluginCatalogItem::TYPE_THEME_PACK,
                        'warning' => PluginCatalogItem::TYPE_BLOCK_PACK,
                        'gray' => PluginCatalogItem::TYPE_PLUGIN,
                    ]),
                Tables\Columns\BadgeColumn::make('status')
                    ->label('Stato')
                    ->formatStateUsing(fn (string $state) => PluginCatalogItem::STATUSES[$state] ?? $state)
                    ->colors([
                        'success' => PluginCatalogItem::STATUS_ACTIVE,
                        'gray' => PluginCatalogItem::STATUS_DRAFT,
                        'danger' => PluginCatalogItem::STATUS_ARCHIVED,
                    ]),
                Tables\Columns\TextColumn::make('entitlements_count')
                    ->label('Agency')
                    ->counts('entitlements')
                    ->badge()
                    ->color('primary'),
                Tables\Columns\TextColumn::make('updated_at')
                    ->label('Modificato')
                    ->dateTime('d/m/Y H:i')
                    ->sortable(),
            ])
            ->filters([
                Tables\Filters\SelectFilter::make('type')
                    ->options(PluginCatalogItem::TYPES),
                Tables\Filters\SelectFilter::make('status')
                    ->options(PluginCatalogItem::STATUSES),
                Tables\Filters\TernaryFilter::make('is_system')
                    ->label('Tipo sorgente')
                    ->trueLabel('Solo sistema')
                    ->falseLabel('Solo manuali'),
            ])
            ->actions([
                Tables\Actions\EditAction::make(),
                Tables\Actions\DeleteAction::make()
                    ->hidden(fn (PluginCatalogItem $record) => $record->entitlements()->exists()),
            ])
            ->emptyStateHeading('Nessun catalog item')
            ->emptyStateIcon('heroicon-o-puzzle-piece');
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListPluginCatalogItems::route('/'),
            'create' => Pages\CreatePluginCatalogItem::route('/create'),
            'edit' => Pages\EditPluginCatalogItem::route('/{record}/edit'),
        ];
    }
}
