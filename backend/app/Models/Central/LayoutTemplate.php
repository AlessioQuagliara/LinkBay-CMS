<?php

declare(strict_types=1);

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Support\Str;

class LayoutTemplate extends Model
{
    protected $connection = 'central';

    public const STATUS_DRAFT = 'draft';

    public const STATUS_PUBLISHED = 'published';

    protected $fillable = [
        'agency_id',
        'name',
        'slug',
        'status',
        'blocks',
    ];

    protected $casts = [
        'blocks' => 'array',
    ];

    // ── Relations ─────────────────────────────────────────────────────────────

    public function agency(): BelongsTo
    {
        return $this->belongsTo(Agency::class);
    }

    public function assignments(): HasMany
    {
        return $this->hasMany(LayoutAssignment::class);
    }

    // ── State helpers ─────────────────────────────────────────────────────────

    public function isDraft(): bool
    {
        return $this->status === self::STATUS_DRAFT;
    }

    public function isPublished(): bool
    {
        return $this->status === self::STATUS_PUBLISHED;
    }

    public function publish(): void
    {
        $this->update(['status' => self::STATUS_PUBLISHED]);
    }

    public function unpublish(): void
    {
        $this->update(['status' => self::STATUS_DRAFT]);
    }

    /**
     * Create an independent copy of this template, scoped to the same agency.
     * The new template starts as draft regardless of the source status.
     */
    public function duplicate(string $newName): self
    {
        $baseSlug = Str::slug($newName);
        $slug = $baseSlug;
        $counter = 1;

        while (
            self::where('agency_id', $this->agency_id)
                ->where('slug', $slug)
                ->exists()
        ) {
            $slug = "{$baseSlug}-{$counter}";
            $counter++;
        }

        return self::create([
            'agency_id' => $this->agency_id,
            'name' => $newName,
            'slug' => $slug,
            'status' => self::STATUS_DRAFT,
            'blocks' => $this->blocks,
        ]);
    }

    // ── Scopes ────────────────────────────────────────────────────────────────

    public function scopePublished($query)
    {
        return $query->where('status', self::STATUS_PUBLISHED);
    }

    public function scopeDraft($query)
    {
        return $query->where('status', self::STATUS_DRAFT);
    }

    public function scopeForAgency($query, int $agencyId)
    {
        return $query->where('agency_id', $agencyId);
    }
}
