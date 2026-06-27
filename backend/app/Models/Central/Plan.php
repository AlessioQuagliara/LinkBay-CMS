<?php

declare(strict_types=1);

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Plan extends Model
{
    use HasFactory;

    protected $connection = 'central';

    protected $fillable = [
        'name',
        'slug',
        'price',
        'billing_interval',
        'stripe_price_id',
        'stripe_product_id',
        'stripe_price_id_monthly',
        'stripe_price_id_yearly',
        'trial_days',
        'features',
        'limits',
        'max_stores',
        'max_members',
        'storage_gb',
        'is_active',
        'sort_order',
    ];

    protected $casts = [
        'features' => 'array',
        'limits' => 'array',
        'is_active' => 'boolean',
        'price' => 'decimal:2',
        'trial_days' => 'integer',
        'max_stores' => 'integer',
        'max_members' => 'integer',
        'storage_gb' => 'integer',
    ];

    public function tenants()
    {
        return $this->hasMany(Tenant::class);
    }

    public function subscriptions()
    {
        return $this->hasMany(Subscription::class);
    }

    public function hasFeature(string $feature): bool
    {
        return in_array($feature, $this->features ?? [], true);
    }

    public function getLimit(string $key, mixed $default = null): mixed
    {
        return $this->limits[$key] ?? $default;
    }

    public function stripePriceFor(string $interval): ?string
    {
        return match ($interval) {
            'monthly' => $this->stripe_price_id_monthly ?? $this->stripe_price_id,
            'yearly' => $this->stripe_price_id_yearly,
            default => $this->stripe_price_id,
        };
    }

    public function priceForInterval(string $interval): float
    {
        if ($interval === 'yearly') {
            return (float) $this->price * 10; // 2 months free
        }

        return (float) $this->price;
    }
}
