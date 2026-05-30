<?php

namespace App\Filament\Agency\Resources;

use App\Filament\Agency\Resources\StoreResource\Pages;
use App\Models\Central\Agency;
use App\Models\Central\AgencyClient;
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
                ->helperText('Es: mionegozio → mionegozio.' . config('app.store_domain', 'yoursite-linkbay-cms.com')),
            Forms\Components\Select::make('status')
                ->options(['active' => 'Attivo', 'suspended' => 'Sospeso'])
                ->default('active'),
            Forms\Components\TextInput::make('admin_email')
                ->label('Email admin negozio')
                ->email()
                ->required()
                ->visibleOn('create'),
            Forms\Components\Select::make('agency_client_id')
                ->label('Cliente')
                ->options(function () {
                    $agency = Agency::fromDomain(request()->getHost());
                    return $agency
                        ? AgencyClient::where('agency_id', $agency->id)
                            ->where('status', 'active')
                            ->orderBy('name')
                            ->pluck('name', 'id')
                        : [];
                })
                ->searchable()
                ->placeholder('Nessun cliente associato')
                ->nullable(),
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
                    ->formatStateUsing(fn ($state) => $state . '.' . config('app.store_domain')),
                Tables\Columns\TextColumn::make('agencyClient.name')
                    ->label('Cliente')
                    ->placeholder('—')
                    ->searchable()
                    ->toggleable(),
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
                        $service = app(TenantProvisioningService::class);
                        $service->registerDomain($record);
                        $service->initializeDatabase($record, $data['admin_email']);
                        Notification::make()->title('Negozio provisionato')->success()->send();
                    }),
                \Filament\Actions\Action::make('access')
                    ->label('Login')
                    ->icon('heroicon-o-arrow-right-on-rectangle')
                    ->url(fn (Tenant $record) => 'http://' . $record->id . '.' . config('app.store_domain') . '/admin')
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
