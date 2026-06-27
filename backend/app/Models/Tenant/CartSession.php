<?php

declare(strict_types=1);

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Model;

class CartSession extends Model
{
    protected $fillable = [
        'session_id',
        'customer_id',
        'expires_at',
        'metadata',
    ];

    protected $casts = [
        'expires_at' => 'datetime',
        'metadata' => 'array',
    ];

    public function cartItems()
    {
        return $this->hasMany(CartItem::class);
    }

    public function customer()
    {
        return $this->belongsTo(Customer::class);
    }

    public function checkoutSession()
    {
        return $this->hasOne(CheckoutSession::class);
    }

    public function scopeActive($query)
    {
        return $query->where(function ($q) {
            $q->whereNull('expires_at')->orWhere('expires_at', '>', now());
        });
    }
}
