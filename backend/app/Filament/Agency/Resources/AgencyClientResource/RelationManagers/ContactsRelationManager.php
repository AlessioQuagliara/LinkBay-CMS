<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources\AgencyClientResource\RelationManagers;

use App\Models\Central\Tenant;
use App\Services\ClientInviteService;
use Filament\Actions\BulkActionGroup;
use Filament\Actions\CreateAction;
use Filament\Actions\DeleteAction;
use Filament\Actions\DeleteBulkAction;
use Filament\Actions\EditAction;
use Filament\Forms;
use Filament\Notifications\Notification;
use Filament\Resources\RelationManagers\RelationManager;
use Filament\Schemas\Schema;
use Filament\Tables;
use Filament\Tables\Table;

class ContactsRelationManager extends RelationManager
{
    protected static string $relationship = 'contacts';

    protected static ?string $title = 'Contatti';

    public function form(Schema $schema): Schema
    {
        return $schema->schema([
            Forms\Components\TextInput::make('name')
                ->label('Nome')
                ->required()
                ->maxLength(255),
            Forms\Components\TextInput::make('email')
                ->label('Email')
                ->email()
                ->required()
                ->maxLength(255),
            Forms\Components\TextInput::make('role')
                ->label('Ruolo')
                ->maxLength(100)
                ->placeholder('Es: CEO, Marketing, Tecnico'),
            Forms\Components\Toggle::make('can_access_tenant')
                ->label('Può accedere agli store')
                ->default(false),
        ]);
    }

    public function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('name')
                    ->label('Nome')
                    ->searchable()
                    ->weight('medium'),
                Tables\Columns\TextColumn::make('email')
                    ->label('Email')
                    ->searchable(),
                Tables\Columns\TextColumn::make('role')
                    ->label('Ruolo')
                    ->placeholder('—'),
                Tables\Columns\IconColumn::make('can_access_tenant')
                    ->label('Accesso store')
                    ->boolean(),
                Tables\Columns\BadgeColumn::make('invite_status')
                    ->label('Invito')
                    ->getStateUsing(function ($record): string {
                        if ($record->can_access_tenant) {
                            return 'attivo';
                        }
                        if ($record->hasPendingInvite()) {
                            return 'in attesa';
                        }
                        if ($record->isInviteExpired()) {
                            return 'scaduto';
                        }

                        return '—';
                    })
                    ->colors([
                        'success' => 'attivo',
                        'warning' => 'in attesa',
                        'danger' => 'scaduto',
                        'gray' => '—',
                    ]),
            ])
            ->headerActions([
                CreateAction::make()->label('Aggiungi contatto'),
            ])
            ->actions([
                Tables\Actions\Action::make('invite')
                    ->label('Invita allo store')
                    ->icon('heroicon-o-paper-airplane')
                    ->color('primary')
                    ->visible(fn ($record) => ! $record->can_access_tenant)
                    ->form(function ($record): array {
                        $client = $record->client()->with('tenants')->first();
                        $stores = $client?->tenants ?? collect();

                        return [
                            Forms\Components\Select::make('tenant_id')
                                ->label('Store da cui accedere')
                                ->options($stores->pluck('name', 'id'))
                                ->required()
                                ->default($stores->count() === 1 ? $stores->first()?->id : null)
                                ->helperText('Il contatto riceverà un link per accedere a questo store.'),
                        ];
                    })
                    ->action(function ($record, array $data): void {
                        $tenant = Tenant::find($data['tenant_id']);

                        if (! $tenant) {
                            Notification::make()
                                ->title('Store non trovato')
                                ->danger()
                                ->send();

                            return;
                        }

                        try {
                            app(ClientInviteService::class)->generateInvite($record, $tenant);

                            Notification::make()
                                ->title('Invito inviato a '.$record->email)
                                ->body('Il link è valido per 72 ore.')
                                ->success()
                                ->send();
                        } catch (\Throwable $e) {
                            Notification::make()
                                ->title('Errore nell\'invio: '.$e->getMessage())
                                ->danger()
                                ->send();
                        }
                    })
                    ->requiresConfirmation(false),

                EditAction::make(),
                DeleteAction::make(),
            ])
            ->bulkActions([
                BulkActionGroup::make([
                    DeleteBulkAction::make(),
                ]),
            ])
            ->emptyStateHeading('Nessun contatto')
            ->emptyStateDescription('Aggiungi i referenti di questo cliente.')
            ->emptyStateIcon('heroicon-o-user-plus');
    }
}
