<?php

declare(strict_types=1);

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;

class AgencyClient extends Model
{
    protected $connection = 'central';

    protected $fillable = [
        'agency_id',
        'name',
        'legal_name',
        'vat_number',
        'country',
        'billing_email',
        'status',
        'notes',
    ];

    // ── Relations ─────────────────────────────────────────────────────────────

    public function agency()
    {
        return $this->belongsTo(Agency::class);
    }

    public function contacts()
    {
        return $this->hasMany(AgencyClientContact::class);
    }

    public function stores()
    {
        return $this->hasMany(Tenant::class);
    }

    // ── Accessors ─────────────────────────────────────────────────────────────

    public function statusLabel(): string
    {
        return match ($this->status) {
            'active'      => 'Attivo',
            'suspended'   => 'Sospeso',
            'offboarded'  => 'Offboarded',
            default       => $this->status,
        };
    }
}
