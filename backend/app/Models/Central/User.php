<?php

declare(strict_types=1);

namespace App\Models\Central;

use Filament\Models\Contracts\FilamentUser;
use Filament\Panel;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;

class User extends Authenticatable implements FilamentUser
{
    use HasFactory, Notifiable;

    protected $connection = 'central';
    protected $table = 'users';

    protected $fillable = [
        'name',
        'email',
        'password',
        'is_super_admin',
    ];

    protected $hidden = [
        'password',
        'remember_token',
    ];

    protected function casts(): array
    {
        return [
            'email_verified_at' => 'datetime',
            'password' => 'hashed',
            'is_super_admin' => 'boolean',
        ];
    }

    public function agency(): \Illuminate\Database\Eloquent\Relations\HasOne
    {
        return $this->hasOne(Agency::class, 'owner_user_id');
    }

    public function canAccessPanel(Panel $panel): bool
    {
        return match ($panel->getId()) {
            // Admin panel: solo super admin
            'admin' => $this->is_super_admin,

            // Agency panel: super admin (per impersonation/support) OPPURE owner dell'agency corrente
            'agency' => $this->is_super_admin || $this->isOwnerOfCurrentAgency(),

            default => false,
        };
    }

    private function isOwnerOfCurrentAgency(): bool
    {
        try {
            $agency = app()->has('current_agency') ? app('current_agency') : null;
            return $agency !== null && (int) $agency->owner_user_id === (int) $this->id;
        } catch (\Throwable) {
            return false;
        }
    }
}
