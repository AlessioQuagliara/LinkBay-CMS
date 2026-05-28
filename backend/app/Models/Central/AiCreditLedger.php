<?php

declare(strict_types=1);

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;

class AiCreditLedger extends Model
{
    protected $connection = 'central';
    protected $table = 'ai_credit_ledger';

    public $timestamps = false;

    const UPDATED_AT = null;

    const TYPE_PURCHASE = 'purchase';
    const TYPE_CONSUMPTION = 'consumption';
    const TYPE_REFUND = 'refund';
    const TYPE_BONUS = 'bonus';

    protected $fillable = [
        'agency_id',
        'tenant_id',
        'amount',
        'balance_after',
        'type',
        'description',
        'stripe_payment_intent_id',
        'metadata',
        'created_at',
    ];

    protected $casts = [
        'amount' => 'integer',
        'balance_after' => 'integer',
        'metadata' => 'array',
        'created_at' => 'datetime',
    ];

    public function agency()
    {
        return $this->belongsTo(Agency::class);
    }
}
