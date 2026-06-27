<?php

declare(strict_types=1);

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\Storage;

class MediaFile extends Model
{
    protected $table = 'media_library';

    protected $fillable = [
        'tenant_id',
        'name',
        'file_name',
        'mime_type',
        'disk',
        'path',
        'size',
        'alt_text',
        'title',
        'collection',
        'metadata',
        'created_by',
    ];

    protected $casts = [
        'metadata' => 'array',
        'size' => 'integer',
    ];

    public function uploader()
    {
        return $this->belongsTo(User::class, 'created_by');
    }

    public function scopeForCollection(Builder $query, string $collection): Builder
    {
        return $query->where('collection', $collection);
    }

    public function url(): string
    {
        try {
            return Storage::disk($this->disk)->url($this->path);
        } catch (\Throwable) {
            return asset('storage/'.$this->path);
        }
    }

    public function isImage(): bool
    {
        return str_starts_with($this->mime_type, 'image/');
    }
}
