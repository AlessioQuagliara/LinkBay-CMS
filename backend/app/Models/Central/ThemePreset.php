<?php

declare(strict_types=1);

namespace App\Models\Central;

use App\Services\ThemeConfigSchema;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Illuminate\Support\Str;

class ThemePreset extends Model
{
    protected $connection = 'central';

    public const STATUS_DRAFT = 'draft';

    public const STATUS_ACTIVE = 'active';

    protected $fillable = [
        'agency_id',
        'name',
        'slug',
        'status',
        'is_system',
        'config',
    ];

    protected $casts = [
        'config' => 'array',
        'is_system' => 'boolean',
    ];

    // ── Relations ─────────────────────────────────────────────────────────────

    public function agency(): BelongsTo
    {
        return $this->belongsTo(Agency::class);
    }

    public function assignments(): HasMany
    {
        return $this->hasMany(ThemeAssignment::class);
    }

    // ── State helpers ─────────────────────────────────────────────────────────

    public function isSystem(): bool
    {
        return (bool) $this->is_system;
    }

    public function isDraft(): bool
    {
        return $this->status === self::STATUS_DRAFT;
    }

    public function isActive(): bool
    {
        return $this->status === self::STATUS_ACTIVE;
    }

    public function activate(): void
    {
        $this->update(['status' => self::STATUS_ACTIVE]);
    }

    public function deactivate(): void
    {
        $this->update(['status' => self::STATUS_DRAFT]);
    }

    /**
     * Return the normalized config. Unknown keys dropped, invalid enums replaced with defaults.
     *
     * @return array<string, mixed>
     */
    public function normalizedConfig(): array
    {
        return ThemeConfigSchema::normalize($this->config ?? []);
    }

    /**
     * Duplicate this preset as an agency-owned draft.
     * System presets can be duplicated; the copy is editable by the agency.
     */
    public function duplicate(int $agencyId, string $newName): self
    {
        $baseSlug = Str::slug($newName);
        $slug = $baseSlug;
        $counter = 1;

        while (
            self::where('agency_id', $agencyId)
                ->where('slug', $slug)
                ->exists()
        ) {
            $slug = "{$baseSlug}-{$counter}";
            $counter++;
        }

        return self::create([
            'agency_id' => $agencyId,
            'name' => $newName,
            'slug' => $slug,
            'status' => self::STATUS_DRAFT,
            'is_system' => false,
            'config' => ThemeConfigSchema::normalize($this->config ?? []),
        ]);
    }

    // ── Scopes ────────────────────────────────────────────────────────────────

    public function scopeActive($query)
    {
        return $query->where('status', self::STATUS_ACTIVE);
    }

    public function scopeSystem($query)
    {
        return $query->where('is_system', true);
    }

    public function scopeForAgency($query, int $agencyId)
    {
        return $query->where('agency_id', $agencyId);
    }

    /**
     * Scope: system presets OR presets owned by the given agency.
     */
    public function scopeVisibleTo($query, int $agencyId)
    {
        return $query->where(function ($q) use ($agencyId) {
            $q->where('is_system', true)->orWhere('agency_id', $agencyId);
        });
    }
}
