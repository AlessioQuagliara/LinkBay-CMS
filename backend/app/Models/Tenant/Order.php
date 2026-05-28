<?php

declare(strict_types=1);

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class Order extends Model
{
    use HasFactory;

    const STATUS_PENDING = 'pending';
    const STATUS_CONFIRMED = 'confirmed';
    const STATUS_PROCESSING = 'processing';
    const STATUS_SHIPPED = 'shipped';
    const STATUS_DELIVERED = 'delivered';
    const STATUS_CANCELLED = 'cancelled';
    const STATUS_REFUNDED = 'refunded';

    protected $fillable = [
        'customer_id',
        'status',
        'total',
        'subtotal',
        'discount_total',
        'shipping_total',
        'shipping_method_id',
        'payment_method',
        'payment_status',
        'tracking_number',
        'notes',
        'shipping_address',
        'billing_address',
        'discount_code_id',
        'metadata',
    ];

    protected $casts = [
        'total' => 'decimal:2',
        'subtotal' => 'decimal:2',
        'discount_total' => 'decimal:2',
        'shipping_total' => 'decimal:2',
        'shipping_address' => 'array',
        'billing_address' => 'array',
        'metadata' => 'array',
    ];

    public function customer()
    {
        return $this->belongsTo(Customer::class);
    }

    public function items()
    {
        return $this->hasMany(OrderItem::class);
    }

    public function shippingMethod()
    {
        return $this->belongsTo(ShippingMethod::class);
    }

    public function discountCode()
    {
        return $this->belongsTo(DiscountCode::class);
    }

    public function scopeByStatus($query, string $status)
    {
        return $query->where('status', $status);
    }
}
