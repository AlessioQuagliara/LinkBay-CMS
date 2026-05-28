<?php

declare(strict_types=1);

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Model;

class OrderItem extends Model
{
    protected $fillable = [
        'order_id',
        'product_id',
        'name',
        'sku',
        'quantity',
        'price',
        'total',
        'metadata',
    ];

    protected $casts = [
        'quantity' => 'integer',
        'price' => 'decimal:2',
        'total' => 'decimal:2',
        'metadata' => 'array',
    ];

    public function order()
    {
        return $this->belongsTo(Order::class);
    }

    public function product()
    {
        return $this->belongsTo(Product::class);
    }
}
