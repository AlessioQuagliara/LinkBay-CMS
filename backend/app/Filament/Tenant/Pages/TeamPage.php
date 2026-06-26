<?php

declare(strict_types=1);

namespace App\Filament\Tenant\Pages;

use App\Models\Tenant\User;
use Filament\Notifications\Notification;
use Filament\Pages\Page;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Password;
use Illuminate\Support\Str;

class TeamPage extends Page
{
    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-user-group';

    protected static ?string $navigationLabel = 'Team';

    protected static string|\UnitEnum|null $navigationGroup = 'Impostazioni';

    protected static ?int $navigationSort = 10;

    protected string $view = 'filament.tenant.pages.team';

    public array $inviteData = [
        'email' => '',
        'role' => User::ROLE_EDITOR,
    ];

    /** @return Collection<int, User> */
    public function getMembers(): Collection
    {
        return User::orderBy('name')->get();
    }

    public function roleLabelFor(string $role): string
    {
        return match ($role) {
            User::ROLE_OWNER => 'Owner',
            User::ROLE_EDITOR => 'Editor',
            User::ROLE_VIEWER => 'Viewer',
            default => ucfirst($role),
        };
    }

    public function roleColorFor(string $role): string
    {
        return match ($role) {
            User::ROLE_OWNER => 'warning',
            User::ROLE_EDITOR => 'primary',
            default => 'gray',
        };
    }

    /**
     * Invite a user by email. If the user already exists in this store the
     * invite is simply re-sent via a password reset link. If the user does
     * not exist a new record is created with a random password and a reset
     * link is dispatched so the invitee can set their own credentials.
     */
    public function inviteUser(): void
    {
        $this->validate([
            'inviteData.email' => ['required', 'email', 'max:255'],
            'inviteData.role' => ['required', 'in:'.implode(',', [
                User::ROLE_EDITOR,
                User::ROLE_VIEWER,
            ])],
        ]);

        $email = $this->inviteData['email'];
        $role = $this->inviteData['role'];

        User::firstOrCreate(
            ['email' => $email],
            [
                'name' => Str::before($email, '@'),
                'password' => Hash::make(Str::random(32)),
                'role' => $role,
            ],
        );

        $status = Password::broker('tenant_users')->sendResetLink(['email' => $email]);

        if ($status === Password::RESET_LINK_SENT) {
            Notification::make()
                ->title('Invito inviato a '.$email)
                ->body('Il link è valido per 24 ore.')
                ->success()
                ->send();

            $this->inviteData = ['email' => '', 'role' => User::ROLE_EDITOR];
        } else {
            Notification::make()
                ->title('Errore nell\'invio email')
                ->body('Verifica la configurazione del mailer.')
                ->danger()
                ->send();
        }
    }

    public function removeUser(int $userId): void
    {
        $current = auth()->user();

        if ($current?->id === $userId) {
            Notification::make()->title('Non puoi rimuovere te stesso')->warning()->send();

            return;
        }

        $target = User::find($userId);
        if (! $target) {
            return;
        }

        if ($target->role === User::ROLE_OWNER) {
            Notification::make()->title('Impossibile rimuovere l\'owner')->warning()->send();

            return;
        }

        $target->delete();
        Notification::make()->title('Utente rimosso')->success()->send();
    }
}
