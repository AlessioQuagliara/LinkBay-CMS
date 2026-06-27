<?php

declare(strict_types=1);

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Model;

class StorePaymentSettings extends Model
{
    protected $fillable = [
        'stripe_account_id',
        'stripe_publishable_key',
        'stripe_secret_key',
        'payment_methods_enabled',
        'currency',
        'capture_method',
        'statement_descriptor',
    ];

    protected $casts = [
        'payment_methods_enabled' => 'array',
        'stripe_secret_key' => 'encrypted',
    ];

    protected $hidden = ['stripe_secret_key'];

    public function isStripeConfigured(): bool
    {
        return ! empty($this->stripe_secret_key);
    }

    public function hasStripeConnect(): bool
    {
        return ! empty($this->stripe_account_id);
    }

    public static function current(): ?self
    {
        return static::first();
    }

    public static function currentOrNew(): self
    {
        return static::firstOrNew([]);
    }
}
