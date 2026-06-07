<?php

declare(strict_types=1);

namespace App\Filament\Agency\Resources;

use App\Filament\Agency\Concerns\ResolvesCurrentAgency;
use App\Filament\Agency\Resources\AgencyMemberResource\Pages;
use App\Models\Central\AgencyMember;
use App\Services\AgencyMemberService;
use Filament\Forms\Components\Select;
use Filament\Forms\Components\TextInput;
use Filament\Notifications\Notification;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;

class AgencyMemberResource extends Resource
{
    use ResolvesCurrentAgency;

    protected static ?string $model = AgencyMember::class;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-user-group';

    protected static ?string $modelLabel = 'Membro';

    protected static ?string $pluralModelLabel = 'Team';

    protected static ?int $navigationSort = 3;

    // ── Authorization ─────────────────────────────────────────────────────────

    public static function canAccess(): bool
    {
        $member = static::currentMemberStatic();

        return $member?->isOwnerOrAdmin() ?? false;
    }

    // ── Scope to current agency ───────────────────────────────────────────────

    public static function getEloquentQuery(): Builder
    {
        $agency = app()->has('current_agency') ? app('current_agency') : null;

        return parent::getEloquentQuery()
            ->with('user')
            ->when(
                $agency,
                fn (Builder $q) => $q->where('agency_id', $agency->id),
                fn (Builder $q) => $q->whereRaw('1=0'),
            );
    }

    // ── Table ─────────────────────────────────────────────────────────────────

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('display_name')
                    ->label('Nome')
                    ->getStateUsing(fn (AgencyMember $record) => $record->user?->name ?? $record->invited_email ?? '—')
                    ->weight('medium')
                    ->searchable(query: fn (Builder $q, string $search) => $q
                        ->whereHas('user', fn ($u) => $u->where('name', 'like', "%{$search}%"))
                        ->orWhere('invited_email', 'like', "%{$search}%")
                    ),

                Tables\Columns\TextColumn::make('email')
                    ->label('Email')
                    ->getStateUsing(fn (AgencyMember $record) => $record->user?->email ?? $record->invited_email ?? '—'),

                Tables\Columns\BadgeColumn::make('role')
                    ->label('Ruolo')
                    ->formatStateUsing(fn (string $state) => match ($state) {
                        AgencyMember::ROLE_OWNER => 'Owner',
                        AgencyMember::ROLE_ADMIN => 'Admin',
                        AgencyMember::ROLE_MEMBER => 'Member',
                        default => ucfirst($state),
                    })
                    ->colors([
                        'warning' => AgencyMember::ROLE_OWNER,
                        'primary' => AgencyMember::ROLE_ADMIN,
                        'gray' => AgencyMember::ROLE_MEMBER,
                    ]),

                Tables\Columns\BadgeColumn::make('status')
                    ->label('Stato')
                    ->formatStateUsing(fn (string $state) => match ($state) {
                        AgencyMember::STATUS_ACTIVE => 'Attivo',
                        AgencyMember::STATUS_PENDING => 'In attesa',
                        AgencyMember::STATUS_SUSPENDED => 'Sospeso',
                        default => ucfirst($state),
                    })
                    ->colors([
                        'success' => AgencyMember::STATUS_ACTIVE,
                        'warning' => AgencyMember::STATUS_PENDING,
                        'danger' => AgencyMember::STATUS_SUSPENDED,
                    ]),

                Tables\Columns\TextColumn::make('invited_at')
                    ->label('Invitato il')
                    ->date('d/m/Y')
                    ->placeholder('—')
                    ->toggleable(isToggledHiddenByDefault: true),

                Tables\Columns\TextColumn::make('accepted_at')
                    ->label('Accettato il')
                    ->date('d/m/Y')
                    ->placeholder('—')
                    ->toggleable(isToggledHiddenByDefault: true),
            ])
            ->headerActions([
                Tables\Actions\Action::make('invite')
                    ->label('Invita membro')
                    ->icon('heroicon-o-paper-airplane')
                    ->color('primary')
                    ->visible(fn () => static::currentMemberStatic()?->isOwnerOrAdmin() ?? false)
                    ->form([
                        TextInput::make('email')
                            ->label('Email')
                            ->email()
                            ->required()
                            ->maxLength(255),
                        Select::make('role')
                            ->label('Ruolo')
                            ->options([
                                AgencyMember::ROLE_ADMIN => 'Admin',
                                AgencyMember::ROLE_MEMBER => 'Member',
                            ])
                            ->default(AgencyMember::ROLE_MEMBER)
                            ->required()
                            ->helperText('Owner può essere assegnato solo dopo che il membro è attivo.'),
                    ])
                    ->action(function (array $data): void {
                        $agency = app()->has('current_agency') ? app('current_agency') : null;
                        $user = auth()->user();

                        if (! $agency || ! $user) {
                            Notification::make()->title('Errore di contesto')->danger()->send();

                            return;
                        }

                        try {
                            app(AgencyMemberService::class)->inviteMember(
                                $agency,
                                $data['email'],
                                $data['role'],
                                $user,
                            );

                            Notification::make()
                                ->title('Invito inviato a '.$data['email'])
                                ->body('Il link è valido per 72 ore.')
                                ->success()
                                ->send();
                        } catch (\Throwable $e) {
                            Notification::make()
                                ->title('Errore: '.$e->getMessage())
                                ->danger()
                                ->send();
                        }
                    }),
            ])
            ->actions([
                Tables\Actions\Action::make('resend_invite')
                    ->label('Reinvia invito')
                    ->icon('heroicon-o-arrow-path')
                    ->color('warning')
                    ->visible(fn (AgencyMember $record) => $record->isPending()
                        && (static::currentMemberStatic()?->isOwnerOrAdmin() ?? false)
                    )
                    ->action(function (AgencyMember $record): void {
                        $agency = app()->has('current_agency') ? app('current_agency') : null;
                        $user = auth()->user();

                        if (! $agency || ! $user || ! $record->invited_email) {
                            return;
                        }

                        try {
                            app(AgencyMemberService::class)->inviteMember(
                                $agency,
                                $record->invited_email,
                                $record->role,
                                $user,
                            );

                            Notification::make()
                                ->title('Invito reinviato a '.$record->invited_email)
                                ->success()
                                ->send();
                        } catch (\Throwable $e) {
                            Notification::make()->title('Errore: '.$e->getMessage())->danger()->send();
                        }
                    }),

                Tables\Actions\Action::make('change_role')
                    ->label('Cambia ruolo')
                    ->icon('heroicon-o-pencil-square')
                    ->color('gray')
                    ->visible(fn (AgencyMember $record) => $record->isActive()
                        && ! $record->isOwner()
                        && (static::currentMemberStatic()?->isOwner() ?? false)
                    )
                    ->form(fn (AgencyMember $record) => [
                        Select::make('role')
                            ->label('Nuovo ruolo')
                            ->options([
                                AgencyMember::ROLE_OWNER => 'Owner (trasferisce proprietà)',
                                AgencyMember::ROLE_ADMIN => 'Admin',
                                AgencyMember::ROLE_MEMBER => 'Member',
                            ])
                            ->default($record->role)
                            ->required(),
                    ])
                    ->action(function (AgencyMember $record, array $data): void {
                        try {
                            app(AgencyMemberService::class)->changeRole($record, $data['role']);
                            Notification::make()->title('Ruolo aggiornato')->success()->send();
                        } catch (\Throwable $e) {
                            Notification::make()->title('Errore: '.$e->getMessage())->danger()->send();
                        }
                    }),

                Tables\Actions\Action::make('suspend')
                    ->label('Sospendi')
                    ->icon('heroicon-o-pause-circle')
                    ->color('warning')
                    ->requiresConfirmation()
                    ->visible(fn (AgencyMember $record) => $record->isActive()
                        && ! $record->isOwner()
                        && (static::currentMemberStatic()?->isOwnerOrAdmin() ?? false)
                    )
                    ->action(function (AgencyMember $record): void {
                        try {
                            app(AgencyMemberService::class)->suspendMember($record);
                            Notification::make()->title('Membro sospeso')->success()->send();
                        } catch (\Throwable $e) {
                            Notification::make()->title('Errore: '.$e->getMessage())->danger()->send();
                        }
                    }),

                Tables\Actions\Action::make('reactivate')
                    ->label('Riattiva')
                    ->icon('heroicon-o-play-circle')
                    ->color('success')
                    ->visible(fn (AgencyMember $record) => $record->status === AgencyMember::STATUS_SUSPENDED
                        && (static::currentMemberStatic()?->isOwnerOrAdmin() ?? false)
                    )
                    ->action(function (AgencyMember $record): void {
                        app(AgencyMemberService::class)->reactivateMember($record);
                        Notification::make()->title('Membro riattivato')->success()->send();
                    }),

                Tables\Actions\Action::make('remove')
                    ->label('Rimuovi')
                    ->icon('heroicon-o-trash')
                    ->color('danger')
                    ->requiresConfirmation()
                    ->visible(fn (AgencyMember $record) => ! $record->isOwner()
                        && (static::currentMemberStatic()?->isOwnerOrAdmin() ?? false)
                    )
                    ->action(function (AgencyMember $record): void {
                        try {
                            app(AgencyMemberService::class)->removeMember($record);
                            Notification::make()->title('Membro rimosso')->success()->send();
                        } catch (\Throwable $e) {
                            Notification::make()->title('Errore: '.$e->getMessage())->danger()->send();
                        }
                    }),
            ])
            ->emptyStateHeading('Nessun membro')
            ->emptyStateDescription('Invita i tuoi collaboratori per gestire insieme i clienti e gli store.')
            ->emptyStateIcon('heroicon-o-user-group');
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListAgencyMembers::route('/'),
        ];
    }
}
