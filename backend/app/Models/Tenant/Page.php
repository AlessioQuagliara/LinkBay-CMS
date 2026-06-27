<?php

declare(strict_types=1);

namespace App\Models\Tenant;

use App\Models\Traits\Translatable;
use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Page extends Model
{
    use HasFactory, Translatable;

    protected $fillable = [
        'slug',
        'title',
        'content',
        'meta_title',
        'meta_description',
        'is_published',
        'sort_order',
        'seo_title',
        'seo_description',
        'og_image_url',
        'blocks',
        'is_homepage',
        'template',
        'published_at',
        'visibility',
        'page_password',
    ];

    protected $casts = [
        'content' => 'array',
        'blocks' => 'array',
        'is_published' => 'boolean',
        'is_homepage' => 'boolean',
        'sort_order' => 'integer',
        'published_at' => 'datetime',
    ];
}
