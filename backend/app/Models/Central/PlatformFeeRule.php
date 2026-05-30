<?php

declare(strict_types=1);

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;

class PlatformFeeRule extends Model
{
    protected $connection = 'central';

    public const UPDATED_AT = null;  // append-only

    protected $fillable = [
        'plan_id',
        'billing_type',
        'fee_pct',
        'fee_type',
        'valid_from',
        'valid_until',
        'description',
        'created_by_user_id',
    ];

    protected $casts = [
        'fee_pct'    => 'decimal:4',
        'valid_from' => 'datetime',
        'valid_until' => 'datetime',
    ];

    public function plan()
    {
        return $this->belongsTo(Plan::class);
    }

    public function feePctAsPercent(): string
    {
        return number_format((float) $this->fee_pct * 100, 1, ',', '.') . '%';
    }
}
