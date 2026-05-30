<?php

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class JobPosition extends Model
{
    protected $connection = 'central';

    protected $fillable = [
        'title',
        'slug',
        'department',
        'location',
        'work_mode',
        'employment_type',
        'summary',
        'description',
        'requirements',
        'responsibilities',
        'nice_to_have',
        'status',
        'featured',
        'sort_order',
        'published_at',
    ];

    protected $casts = [
        'requirements'    => 'array',
        'responsibilities' => 'array',
        'nice_to_have'    => 'array',
        'featured'        => 'boolean',
        'published_at'    => 'datetime',
    ];

    public function applications(): HasMany
    {
        return $this->hasMany(JobApplication::class);
    }

    public function scopePublished($query)
    {
        return $query->where('status', 'published');
    }
}
