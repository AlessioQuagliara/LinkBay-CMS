<?php

declare(strict_types=1);

namespace App\Models\Tenant;

use Illuminate\Contracts\Auth\MustVerifyEmail;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;

class Customer extends Authenticatable implements MustVerifyEmail
{
    use HasFactory;
    use Notifiable;

    protected $fillable = [
        'name',
        'email',
        'password',
        'status',
        'phone',
        'address',
        'notes',
        'tags',
        'total_spent',
        'orders_count',
        'accepts_marketing',
        'last_login_at',
        'default_shipping_address_id',
        'default_billing_address_id',
    ];

    protected $hidden = [
        'password',
        'remember_token',
    ];

    protected $casts = [
        'address' => 'array',
        'tags' => 'array',
        'total_spent' => 'decimal:2',
        'orders_count' => 'integer',
        'accepts_marketing' => 'boolean',
        'email_verified_at' => 'datetime',
        'last_login_at' => 'datetime',
    ];

    public function orders(): HasMany
    {
        return $this->hasMany(Order::class);
    }

    public function addresses(): HasMany
    {
        return $this->hasMany(CustomerAddress::class);
    }

    public function defaultShippingAddress(): BelongsTo
    {
        return $this->belongsTo(CustomerAddress::class, 'default_shipping_address_id');
    }

    public function defaultBillingAddress(): BelongsTo
    {
        return $this->belongsTo(CustomerAddress::class, 'default_billing_address_id');
    }

    public function wishlistProducts(): BelongsToMany
    {
        return $this->belongsToMany(Product::class, 'customer_wishlist')
            ->withTimestamps()
            ->orderByPivot('created_at', 'desc');
    }
}
