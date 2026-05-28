<?php

declare(strict_types=1);

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class AiCreditPackage extends Model
{
    use HasFactory;

    protected $connection = 'central';

    protected $fillable = [
        'name',
        'credits',
        'price_cents',
        'stripe_price_id',
        'is_active',
        'sort_order',
    ];

    protected $casts = [
        'credits' => 'integer',
        'price_cents' => 'integer',
        'is_active' => 'boolean',
        'sort_order' => 'integer',
    ];

    public function priceFormatted(): string
    {
        return '€' . number_format($this->price_cents / 100, 2, ',', '.');
    }

    public function scopeActive($query)
    {
        return $query->where('is_active', true)->orderBy('sort_order');
    }
}
