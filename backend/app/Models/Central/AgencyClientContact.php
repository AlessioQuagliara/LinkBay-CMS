<?php

declare(strict_types=1);

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class AgencyClientContact extends Model
{
    protected $connection = 'central';

    protected $fillable = [
        'agency_client_id',
        'user_id',
        'name',
        'email',
        'role',
        'can_access_tenant',
        'invite_token',
        'invite_tenant_id',
        'invite_expires_at',
    ];

    protected $casts = [
        'can_access_tenant' => 'boolean',
        'invite_expires_at' => 'datetime',
    ];

    public function client(): BelongsTo
    {
        return $this->belongsTo(AgencyClient::class, 'agency_client_id');
    }

    public function inviteTenant(): BelongsTo
    {
        return $this->belongsTo(Tenant::class, 'invite_tenant_id');
    }

    public function hasPendingInvite(): bool
    {
        return $this->invite_token !== null
            && $this->invite_expires_at !== null
            && $this->invite_expires_at->isFuture();
    }

    public function isInviteExpired(): bool
    {
        return $this->invite_token !== null
            && $this->invite_expires_at !== null
            && $this->invite_expires_at->isPast();
    }
}
