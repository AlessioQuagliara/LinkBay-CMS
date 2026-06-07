<?php

declare(strict_types=1);

namespace App\Models\Central;

use Filament\Models\Contracts\FilamentUser;
use Filament\Panel;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Database\Eloquent\Relations\HasOne;
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

    public function agency(): HasOne
    {
        return $this->hasOne(Agency::class, 'owner_user_id');
    }

    public function agencyMemberships(): HasMany
    {
        return $this->hasMany(AgencyMember::class);
    }

    public function canAccessPanel(Panel $panel): bool
    {
        return match ($panel->getId()) {
            'admin' => $this->is_super_admin,
            'agency' => $this->is_super_admin || $this->isActiveMemberOfCurrentAgency(),
            default => false,
        };
    }

    /**
     * Returns true when the user has an active AgencyMember record for the
     * current request's agency (resolved by EnsureValidAgencyDomain).
     */
    public function isActiveMemberOfCurrentAgency(): bool
    {
        try {
            $agency = app()->has('current_agency') ? app('current_agency') : null;

            if (! $agency) {
                return false;
            }

            return AgencyMember::where('agency_id', $agency->id)
                ->where('user_id', $this->id)
                ->where('status', AgencyMember::STATUS_ACTIVE)
                ->exists();
        } catch (\Throwable) {
            return false;
        }
    }

    /**
     * Returns the current user's AgencyMember record for the active agency, or null.
     */
    public function membershipForCurrentAgency(): ?AgencyMember
    {
        try {
            $agency = app()->has('current_agency') ? app('current_agency') : null;

            if (! $agency) {
                return null;
            }

            return AgencyMember::where('agency_id', $agency->id)
                ->where('user_id', $this->id)
                ->where('status', AgencyMember::STATUS_ACTIVE)
                ->first();
        } catch (\Throwable) {
            return null;
        }
    }
}
