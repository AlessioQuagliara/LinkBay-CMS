<?php

declare(strict_types=1);

namespace App\Models\Central;

use App\Plugins\PluginRegistry;
use App\Services\ThemeConfigSchema;
use App\Services\ThemeForkResolver;
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
        'parent_theme_slug',
        'override_config',
    ];

    protected $casts = [
        'config' => 'array',
        'is_system' => 'boolean',
        'override_config' => 'array',
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

    public function isFork(): bool
    {
        return $this->parent_theme_slug !== null;
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
     * Return the authoritative renderable config.
     *
     * - Standalone preset: normalize(config)
     * - Fork: merge(parent registry defaultConfig, override_config)
     *   Locked fields always come from the parent; overrides are applied on top.
     *   This means the fork always reflects the current state of the parent theme,
     *   even if the parent was updated after the fork was created.
     *
     * @return array<string, mixed>
     */
    public function resolvedConfig(): array
    {
        if (! $this->isFork()) {
            return ThemeConfigSchema::normalize($this->config ?? []);
        }

        $parentDef = app(PluginRegistry::class)->getTheme($this->parent_theme_slug);
        $baseConfig = ThemeConfigSchema::normalize($parentDef?->defaultConfig ?? []);

        return ThemeForkResolver::applyOverrides($baseConfig, $this->override_config ?? []);
    }

    /**
     * Return the normalized config. Delegates to resolvedConfig() so forks
     * automatically use inheritance + override logic.
     *
     * @return array<string, mixed>
     */
    public function normalizedConfig(): array
    {
        return $this->resolvedConfig();
    }

    /**
     * Duplicate this preset as a flat agency-owned draft (no inheritance link).
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
            'config' => $this->resolvedConfig(),
        ]);
    }

    /**
     * Create an inheriting fork of this system theme.
     * The fork starts with no overrides — all values inherited from the parent.
     * Only forkable from system presets; enforced by ThemeForkResolver::canFork().
     */
    public function fork(int $agencyId, string $name): self
    {
        $baseSlug = Str::slug($name);
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
            'name' => $name,
            'slug' => $slug,
            'status' => self::STATUS_DRAFT,
            'is_system' => false,
            'parent_theme_slug' => $this->slug,
            'override_config' => [],
            'config' => $this->resolvedConfig(), // snapshot for fallback
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
