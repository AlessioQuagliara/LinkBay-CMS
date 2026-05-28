<?php

namespace App\Filament\Agency\Resources;

use App\Filament\Agency\Resources\StoreResource\Pages;
use App\Models\Central\Agency;
use App\Models\Central\Tenant;
use App\Services\TenantProvisioningService;
use Filament\Forms;
use Filament\Schemas\Schema;

use Filament\Notifications\Notification;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;

class StoreResource extends Resource
{
    protected static ?string $model = Tenant::class;
    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-shopping-bag';
    protected static ?string $modelLabel = 'Negozio';
    protected static ?string $pluralModelLabel = 'Negozi';

    public static function form(Schema $schema): Schema
    {
        return $schema->schema([
            Forms\Components\TextInput::make('name')->label('Nome negozio')->required(),
            Forms\Components\TextInput::make('id')
                ->label('Subdomain')
                ->required()
                ->unique(Tenant::class, 'id', ignoreRecord: true)
                ->helperText('Es: mionegozio → mionegozio.linkbay-cms.com'),
            Forms\Components\Select::make('status')
                ->options(['active' => 'Attivo', 'suspended' => 'Sospeso'])
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
            ->modifyQueryUsing(function ($query) {
                $agency = Agency::fromDomain(request()->getHost());
                return $agency ? $query->where('agency_id', $agency->id) : $query;
            })
            ->columns([
                Tables\Columns\TextColumn::make('name')->label('Nome')->searchable(),
                Tables\Columns\TextColumn::make('id')
                    ->label('Dominio')
                    ->formatStateUsing(fn ($state) => $state . '.linkbay-cms.com'),
                Tables\Columns\TextColumn::make('status')
                    ->label('Stato')
                    ->badge()
                    ->color(fn ($state) => $state === 'active' ? 'success' : 'warning'),
                Tables\Columns\TextColumn::make('created_at')->label('Creato')->date('d/m/Y'),
            ])
            ->actions([
                \Filament\Actions\EditAction::make(),
                \Filament\Actions\Action::make('provision')
                    ->label('Provisioning')
                    ->icon('heroicon-o-server')
                    ->color('success')
                    ->requiresConfirmation()
                    ->form([
                        Forms\Components\TextInput::make('admin_email')
                            ->label('Email admin')
                            ->email()
                            ->required(),
                    ])
                    ->action(function (Tenant $record, array $data) {
                        $agency = Agency::fromDomain(request()->getHost());
                        app(TenantProvisioningService::class)->provision([
                            'name' => $record->name,
                            'domain' => $record->id,
                            'admin_email' => $data['admin_email'],
                            'agency_id' => $agency?->id,
                        ]);
                        Notification::make()->title('Negozio provisionato')->success()->send();
                    }),
                \Filament\Actions\Action::make('access')
                    ->label('Accedi')
                    ->icon('heroicon-o-arrow-right-on-rectangle')
                    ->url(fn (Tenant $record) => 'http://' . $record->id . '.linkbay-cms.com/admin')
                    ->openUrlInNewTab(),
            ]);
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListStores::route('/'),
            'create' => Pages\CreateStore::route('/create'),
            'edit' => Pages\EditStore::route('/{record}/edit'),
        ];
    }
}
