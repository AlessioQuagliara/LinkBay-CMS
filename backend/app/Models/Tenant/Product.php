<?php

declare(strict_types=1);

namespace App\Models\Tenant;

use App\Models\Traits\Translatable;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\SoftDeletes;

class Product extends Model
{
    use HasFactory, SoftDeletes, Translatable;

    protected $fillable = [
        'name',
        'slug',
        'description',
        'price',
        'compare_price',
        'compare_at_price',
        'cost_per_item',
        'stock',
        'track_quantity',
        'quantity',
        'sku',
        'barcode',
        'collection_id',
        'images',
        'is_active',
        'weight',
        'weight_unit',
        'requires_shipping',
        'is_taxable',
        'tax_class',
        'metadata',
        'seo_title',
        'seo_description',
        'seo_keywords',
    ];

    protected $casts = [
        'images' => 'array',
        'metadata' => 'array',
        'price' => 'decimal:2',
        'compare_price' => 'decimal:2',
        'compare_at_price' => 'decimal:2',
        'cost_per_item' => 'decimal:2',
        'is_active' => 'boolean',
        'track_quantity' => 'boolean',
        'requires_shipping' => 'boolean',
        'is_taxable' => 'boolean',
        'stock' => 'integer',
        'quantity' => 'integer',
        'weight' => 'decimal:2',
    ];

    public function collection()
    {
        return $this->belongsTo(Collection::class);
    }

    public function orderItems()
    {
        return $this->hasMany(OrderItem::class);
    }

    public function productImages()
    {
        return $this->hasMany(ProductImage::class)->orderBy('sort_order');
    }

    public function categories()
    {
        return $this->belongsToMany(Category::class, 'product_categories');
    }

    public function cartItems()
    {
        return $this->hasMany(CartItem::class);
    }

    public function scopeActive($query)
    {
        return $query->where('is_active', true);
    }
}
