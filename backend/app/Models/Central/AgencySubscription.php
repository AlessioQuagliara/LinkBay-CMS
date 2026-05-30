<?php

declare(strict_types=1);

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;

class AgencySubscription extends Model
{
    protected $connection = 'central';

    protected $fillable = [
        'agency_id',
        'plan_id',
        'stripe_subscription_id',
        'stripe_customer_id',
        'status',
        'billing_type',
        'current_period_start',
        'current_period_end',
        'trial_ends_at',
        'cancelled_at',
    ];

    protected $casts = [
        'current_period_start' => 'datetime',
        'current_period_end'   => 'datetime',
        'trial_ends_at'        => 'datetime',
        'cancelled_at'         => 'datetime',
    ];

    public function agency()
    {
        return $this->belongsTo(Agency::class);
    }

    public function plan()
    {
        return $this->belongsTo(Plan::class);
    }

    public function isActive(): bool
    {
        return in_array($this->status, ['active', 'trialing'], true);
    }

    public function isLifetime(): bool
    {
        return $this->billing_type === 'lifetime';
    }

    public function isPastDue(): bool
    {
        return $this->status === 'past_due';
    }

    public function renewalLabel(): string
    {
        if ($this->isLifetime()) {
            return 'Lifetime — non scade';
        }

        if (!$this->current_period_end) {
            return '—';
        }

        return 'Rinnovo il ' . $this->current_period_end->format('d/m/Y');
    }
}
