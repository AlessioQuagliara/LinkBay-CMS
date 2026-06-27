<?php

declare(strict_types=1);

namespace App\Models\Tenant;

use App\Models\Traits\Translatable;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Collection extends Model
{
    use HasFactory, Translatable;

    protected $fillable = [
        'name',
        'slug',
        'description',
        'parent_id',
        'image',
        'sort_order',
        'is_active',
    ];

    protected $casts = [
        'is_active' => 'boolean',
        'sort_order' => 'integer',
    ];

    public function parent()
    {
        return $this->belongsTo(Collection::class, 'parent_id');
    }

    public function children()
    {
        return $this->hasMany(Collection::class, 'parent_id');
    }

    public function products()
    {
        return $this->hasMany(Product::class);
    }
}
