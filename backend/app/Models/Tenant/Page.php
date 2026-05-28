<?php

declare(strict_types=1);

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Factories\HasFactory;

class Page extends Model
{
    use HasFactory;

    protected $fillable = [
        'slug',
        'title',
        'content',
        'meta_title',
        'meta_description',
        'is_published',
        'sort_order',
    ];

    protected $casts = [
        'content' => 'array',
        'is_published' => 'boolean',
        'sort_order' => 'integer',
    ];
}
