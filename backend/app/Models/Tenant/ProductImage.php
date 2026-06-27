<?php

declare(strict_types=1);

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Model;

class ProductImage extends Model
{
    protected $fillable = [
        'product_id',
        'url',
        'alt_text',
        'sort_order',
        'is_primary',
    ];

    protected $casts = [
        'sort_order' => 'integer',
        'is_primary' => 'boolean',
    ];

    public function product()
    {
        return $this->belongsTo(Product::class);
    }
}
