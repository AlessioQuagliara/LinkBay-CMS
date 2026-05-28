<?php

declare(strict_types=1);

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class ShippingMethod extends Model
{
    use HasFactory;

    protected $fillable = [
        'name',
        'carrier',
        'price',
        'rules',
        'is_active',
        'estimated_days',
    ];

    protected $casts = [
        'price' => 'decimal:2',
        'rules' => 'array',
        'is_active' => 'boolean',
        'estimated_days' => 'integer',
    ];

    public function orders()
    {
        return $this->hasMany(Order::class);
    }
}
