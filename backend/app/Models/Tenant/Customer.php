<?php

declare(strict_types=1);

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class Customer extends Model
{
    use HasFactory;

    protected $fillable = [
        'name',
        'email',
        'phone',
        'address',
        'notes',
        'tags',
        'total_spent',
        'orders_count',
    ];

    protected $casts = [
        'address' => 'array',
        'tags' => 'array',
        'total_spent' => 'decimal:2',
        'orders_count' => 'integer',
    ];

    public function orders()
    {
        return $this->hasMany(Order::class);
    }
}
