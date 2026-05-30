<?php

declare(strict_types=1);

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;

class BillingEvent extends Model
{
    protected $connection = 'central';

    public const UPDATED_AT = null;  // append-only

    protected $fillable = [
        'agency_id',
        'tenant_id',
        'stripe_event_id',
        'event_type',
        'payload',
        'processed_at',
        'error',
    ];

    protected $casts = [
        'payload'      => 'array',
        'processed_at' => 'datetime',
        'created_at'   => 'datetime',
    ];

    public function agency()
    {
        return $this->belongsTo(Agency::class);
    }

    public function isProcessed(): bool
    {
        return $this->processed_at !== null;
    }

    public function markProcessed(): void
    {
        $this->update(['processed_at' => now()]);
    }

    public function markFailed(string $error): void
    {
        $this->update(['error' => $error]);
    }
}
