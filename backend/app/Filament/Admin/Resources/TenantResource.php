<?php

namespace App\Filament\Admin\Resources;

use App\Filament\Admin\Resources\TenantResource\Pages;
use App\Models\Central\Tenant;
use App\Services\TenantProvisioningService;
use Filament\Forms;
use Filament\Schemas\Schema;

use Filament\Notifications\Notification;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;

class TenantResource extends Resource
{
    protected static ?string $model = Tenant::class;
    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-building-office-2';
    protected static string|\UnitEnum|null $navigationGroup = 'Tenancy';
    protected static ?string $modelLabel = 'Tenant';
    protected static ?string $pluralModelLabel = 'Tenant';

    public static function form(Schema $schema): Schema
    {
        return $schema->schema([
            Forms\Components\TextInput::make('name')
                ->label('Nome negozio')
                ->required(),
            Forms\Components\TextInput::make('id')
                ->label('Domain / ID')
                ->required()
                ->unique(Tenant::class, 'id', ignoreRecord: true)
                ->helperText('Es: cliente1 → cliente1.linkbay-cms.com'),
            Forms\Components\Select::make('plan_id')
                ->label('Piano')
                ->relationship('plan', 'name')
                ->searchable()
                ->preload(),
            Forms\Components\Select::make('agency_id')
                ->label('Agenzia')
                ->relationship('agency', 'name')
                ->searchable()
                ->preload()
                ->nullable(),
            Forms\Components\Select::make('status')
                ->label('Stato')
                ->options(['active' => 'Attivo', 'suspended' => 'Sospeso', 'cancelled' => 'Cancellato'])
                ->default('active'),
            Forms\Components\TextInput::make('admin_email')
                ->label('Email admin negozio')
                ->email()
                ->required()
                ->visibleOn('create'),
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
                Tables\Columns\TextColumn::make('id')
                    ->label('Domain')
                    ->formatStateUsing(fn ($state) => $state . '.linkbay-cms.com'),
                Tables\Columns\TextColumn::make('plan.name')
                    ->label('Piano')
                    ->badge()
                    ->color('info'),
                Tables\Columns\TextColumn::make('status')
                    ->label('Stato')
                    ->badge()
                    ->color(fn ($state) => match($state) {
                        'active' => 'success',
                        'suspended' => 'warning',
                        'cancelled' => 'danger',
                        default => 'gray',
                    }),
                Tables\Columns\TextColumn::make('created_at')
                    ->label('Creato')
                    ->date('d/m/Y')
                    ->sortable(),
            ])
            ->filters([
                Tables\Filters\SelectFilter::make('status')
                    ->options(['active' => 'Attivo', 'suspended' => 'Sospeso', 'cancelled' => 'Cancellato']),
            ])
            ->actions([
                \Filament\Actions\EditAction::make(),
                \Filament\Actions\Action::make('provision')
                    ->label('Provisioning')
                    ->icon('heroicon-o-server')
                    ->color('success')
                    ->requiresConfirmation()
                    ->action(function (Tenant $record) {
                        app(TenantProvisioningService::class)->provision([
                            'name' => $record->name,
                            'domain' => $record->id,
                        ]);
                        Notification::make()->title('Tenant provisionato')->success()->send();
                    }),
                \Filament\Actions\Action::make('suspend')
                    ->label('Sospendi')
                    ->icon('heroicon-o-pause-circle')
                    ->color('warning')
                    ->requiresConfirmation()
                    ->action(fn (Tenant $record) => $record->update(['status' => 'suspended'])),
                \Filament\Actions\DeleteAction::make(),
            ])
            ->bulkActions([
                \Filament\Actions\BulkActionGroup::make([
                    \Filament\Actions\DeleteBulkAction::make(),
                ]),
            ])
            ->defaultSort('created_at', 'desc');
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListTenants::route('/'),
            'create' => Pages\CreateTenants::route('/create'),
            'edit' => Pages\EditTenants::route('/{record}/edit'),
        ];
    }
}
