<?php

declare(strict_types=1);

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;

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
    ];

    protected $casts = [
        'can_access_tenant' => 'boolean',
    ];

    public function client()
    {
        return $this->belongsTo(AgencyClient::class, 'agency_client_id');
    }
}
