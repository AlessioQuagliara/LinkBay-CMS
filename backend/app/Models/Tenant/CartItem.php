<?php

declare(strict_types=1);

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Model;

class CartItem extends Model
{
    protected $fillable = [
        'cart_session_id',
        'product_id',
        'variant_id',
        'quantity',
        'unit_price',
        'metadata',
    ];

    protected $casts = [
        'quantity' => 'integer',
        'unit_price' => 'decimal:2',
        'metadata' => 'array',
    ];

    public function cartSession()
    {
        return $this->belongsTo(CartSession::class);
    }

    public function product()
    {
        return $this->belongsTo(Product::class);
    }

    public function getLineTotalAttribute(): float
    {
        return (float) $this->unit_price * $this->quantity;
    }
}
