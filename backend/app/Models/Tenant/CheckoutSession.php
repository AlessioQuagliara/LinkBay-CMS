<?php

declare(strict_types=1);

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Model;

class CheckoutSession extends Model
{
    const STATUS_PENDING = 'pending';

    const STATUS_PROCESSING = 'processing';

    const STATUS_COMPLETED = 'completed';

    const STATUS_ABANDONED = 'abandoned';

    protected $fillable = [
        'cart_session_id',
        'customer_id',
        'status',
        'shipping_address',
        'billing_address',
        'shipping_method_id',
        'discount_code_id',
        'subtotal',
        'shipping_amount',
        'discount_amount',
        'tax_amount',
        'total',
        'stripe_payment_intent_id',
        'stripe_payment_status',
        'completed_at',
    ];

    protected $casts = [
        'shipping_address' => 'array',
        'billing_address' => 'array',
        'subtotal' => 'decimal:2',
        'shipping_amount' => 'decimal:2',
        'discount_amount' => 'decimal:2',
        'tax_amount' => 'decimal:2',
        'total' => 'decimal:2',
        'completed_at' => 'datetime',
    ];

    public function cartSession()
    {
        return $this->belongsTo(CartSession::class);
    }

    public function customer()
    {
        return $this->belongsTo(Customer::class);
    }

    public function shippingMethod()
    {
        return $this->belongsTo(ShippingMethod::class);
    }

    public function discountCode()
    {
        return $this->belongsTo(DiscountCode::class);
    }
}
