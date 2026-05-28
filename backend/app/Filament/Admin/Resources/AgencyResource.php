<?php

namespace App\Filament\Admin\Resources;

use App\Filament\Admin\Resources\AgencyResource\Pages;
use App\Models\Central\Agency;
use App\Services\AiCreditsService;
use Filament\Forms;
use Filament\Notifications\Notification;
use Filament\Resources\Resource;
use Filament\Schemas\Schema;
use Filament\Tables;
use Filament\Tables\Table;

class AgencyResource extends Resource
{
    protected static ?string $model = Agency::class;
    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-building-library';
    protected static string|\UnitEnum|null $navigationGroup = 'Tenancy';
    protected static ?string $modelLabel = 'Agenzia';
    protected static ?string $pluralModelLabel = 'Agenzie';

    public static function form(Schema $schema): Schema
    {
        return $schema->schema([
            Forms\Components\Section::make('Anagrafica')
                ->schema([
                    Forms\Components\TextInput::make('name')->label('Nome')->required(),
                    Forms\Components\TextInput::make('slug')->label('Slug')->required()
                        ->unique(Agency::class, 'slug', ignoreRecord: true),
                    Forms\Components\TextInput::make('brand_name')->label('Brand Name')->required(),
                    Forms\Components\TextInput::make('owner_email')
                        ->label('Email owner')
                        ->email()
                        ->dehydrated(false)
                        ->visibleOn('create'),
                ])->columns(2),

            Forms\Components\Section::make('Piano & Billing')
                ->schema([
                    Forms\Components\Select::make('plan_id')
                        ->label('Piano')
                        ->relationship('plan', 'name')
                        ->searchable()
                        ->preload()
                        ->required(),
                    Forms\Components\Select::make('billing_type')
                        ->label('Tipo fatturazione')
                        ->options([
                            'monthly' => 'Mensile',
                            'yearly' => 'Annuale',
                            'lifetime' => 'Lifetime (AppSumo LTD)',
                        ])
                        ->default('monthly')
                        ->required()
                        ->live(),
                    Forms\Components\TextInput::make('ltdcode')
                        ->label('Codice AppSumo LTD')
                        ->visible(fn (Forms\Get $get) => $get('billing_type') === 'lifetime')
                        ->unique(Agency::class, 'ltdcode', ignoreRecord: true),
                    Forms\Components\Select::make('status')
                        ->options(['active' => 'Attiva', 'suspended' => 'Sospesa', 'cancelled' => 'Cancellata'])
                        ->default('active')
                        ->required(),
                ])->columns(2),

            Forms\Components\Section::make('Stripe Connect')
                ->schema([
                    Forms\Components\TextInput::make('stripe_connect_account_id')
                        ->label('Stripe Account ID')
                        ->disabled(),
                    Forms\Components\Toggle::make('stripe_connect_onboarded')
                        ->label('KYC completato')
                        ->disabled(),
                ])->columns(2),
        ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('name')->label('Nome')->searchable()->sortable(),
                Tables\Columns\TextColumn::make('custom_domain')
                    ->label('Dominio')
                    ->state(fn ($record) => $record->custom_domain ?? $record->slug . '.linkbay-cms.com')
                    ->toggleable(),
                Tables\Columns\TextColumn::make('plan.name')->label('Piano')->badge()->color('info'),
                Tables\Columns\TextColumn::make('billing_type')
                    ->label('Billing')
                    ->badge()
                    ->color(fn ($state) => match($state) {
                        'monthly' => 'info',
                        'yearly' => 'success',
                        'lifetime' => 'warning',
                        default => 'gray',
                    })
                    ->formatStateUsing(fn ($state) => match($state) {
                        'monthly' => 'Mensile', 'yearly' => 'Annuale',
                        'lifetime' => 'Lifetime', default => $state,
                    }),
                Tables\Columns\TextColumn::make('tenants_count')
                    ->label('Negozi')
                    ->counts('tenants')
                    ->badge()
                    ->color('primary'),
                Tables\Columns\TextColumn::make('credit_balance')
                    ->label('Crediti AI')
                    ->state(fn ($record) => number_format($record->creditBalance()))
                    ->icon('heroicon-o-sparkles'),
                Tables\Columns\IconColumn::make('stripe_connect_onboarded')
                    ->label('Stripe')
                    ->boolean(),
                Tables\Columns\TextColumn::make('status')
                    ->badge()
                    ->color(fn ($state) => match($state) {
                        'active' => 'success', 'suspended' => 'warning',
                        'cancelled' => 'danger', default => 'gray',
                    }),
                Tables\Columns\TextColumn::make('created_at')
                    ->label('Creata')->date('d/m/Y')->sortable()
                    ->toggleable(isToggledHiddenByDefault: true),
            ])
            ->filters([
                Tables\Filters\SelectFilter::make('status')
                    ->options(['active' => 'Attiva', 'suspended' => 'Sospesa', 'cancelled' => 'Cancellata']),
                Tables\Filters\SelectFilter::make('billing_type')
                    ->options(['monthly' => 'Mensile', 'yearly' => 'Annuale', 'lifetime' => 'Lifetime']),
            ])
            ->actions([
                \Filament\Actions\EditAction::make(),
                \Filament\Actions\Action::make('impersonate')
                    ->label('Accedi')
                    ->icon('heroicon-o-arrow-right-on-rectangle')
                    ->url(fn (Agency $record) => 'http://' . $record->panelDomain() . '/dashboard')
                    ->openUrlInNewTab(),
                \Filament\Actions\Action::make('add_bonus_credits')
                    ->label('Bonus AI')
                    ->icon('heroicon-o-sparkles')
                    ->color('warning')
                    ->form([
                        Forms\Components\TextInput::make('credits')->label('Crediti')->numeric()->required()->minValue(1),
                        Forms\Components\TextInput::make('reason')->label('Motivo')->required(),
                    ])
                    ->action(function (Agency $record, array $data) {
                        app(AiCreditsService::class)->addBonus($record, (int) $data['credits'], $data['reason']);
                        Notification::make()->title("Bonus {$data['credits']} crediti aggiunto")->success()->send();
                    }),
                \Filament\Actions\Action::make('suspend')
                    ->label('Sospendi')->icon('heroicon-o-pause-circle')->color('warning')
                    ->requiresConfirmation()
                    ->visible(fn (Agency $r) => $r->status === 'active')
                    ->action(fn (Agency $r) => $r->update(['status' => 'suspended'])),
                \Filament\Actions\Action::make('reactivate')
                    ->label('Riattiva')->icon('heroicon-o-play-circle')->color('success')
                    ->visible(fn (Agency $r) => $r->status !== 'active')
                    ->action(fn (Agency $r) => $r->update(['status' => 'active'])),
                \Filament\Actions\DeleteAction::make(),
            ])
            ->defaultSort('created_at', 'desc');
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListAgencies::route('/'),
            'create' => Pages\CreateAgencies::route('/create'),
            'edit' => Pages\EditAgencies::route('/{record}/edit'),
        ];
    }
}
