<?php

declare(strict_types=1);

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;

class PayoutRecord extends Model
{
    protected $connection = 'central';

    public const STATUS_PENDING = 'pending';

    public const STATUS_IN_TRANSIT = 'in_transit';

    public const STATUS_PAID = 'paid';

    public const STATUS_FAILED = 'failed';

    public const STATUS_CANCELLED = 'cancelled';

    protected $fillable = [
        'agency_id',
        'stripe_payout_id',
        'stripe_connect_account_id',
        'amount_cents',
        'currency',
        'status',
        'arrival_date',
        'failure_reason',
        'metadata',
    ];

    protected $casts = [
        'arrival_date' => 'date',
        'metadata' => 'array',
    ];

    public function agency()
    {
        return $this->belongsTo(Agency::class);
    }

    public function amountFormatted(): string
    {
        return number_format($this->amount_cents / 100, 2, ',', '.').' '.strtoupper($this->currency);
    }

    public function statusLabel(): string
    {
        return match ($this->status) {
            self::STATUS_PENDING => 'In attesa',
            self::STATUS_IN_TRANSIT => 'In transito',
            self::STATUS_PAID => 'Pagato',
            self::STATUS_FAILED => 'Fallito',
            self::STATUS_CANCELLED => 'Annullato',
            default => ucfirst($this->status),
        };
    }

    /**
     * Returns Tailwind color tokens used in the Blade badge.
     */
    public function statusColor(): string
    {
        return match ($this->status) {
            self::STATUS_PAID => 'green',
            self::STATUS_IN_TRANSIT => 'blue',
            self::STATUS_PENDING => 'yellow',
            self::STATUS_FAILED => 'red',
            self::STATUS_CANCELLED => 'gray',
            default => 'gray',
        };
    }
}
