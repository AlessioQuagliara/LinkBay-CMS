<?php

declare(strict_types=1);

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class PluginCatalogItem extends Model
{
    protected $connection = 'central';

    public const TYPE_FEATURE = 'feature';

    public const TYPE_THEME_PACK = 'theme_pack';

    public const TYPE_BLOCK_PACK = 'block_pack';

    public const TYPE_PLUGIN = 'plugin';

    public const STATUS_DRAFT = 'draft';

    public const STATUS_ACTIVE = 'active';

    public const STATUS_ARCHIVED = 'archived';

    public const TYPES = [
        self::TYPE_FEATURE => 'Feature',
        self::TYPE_THEME_PACK => 'Theme Pack',
        self::TYPE_BLOCK_PACK => 'Block Pack',
        self::TYPE_PLUGIN => 'Plugin',
    ];

    public const STATUSES = [
        self::STATUS_DRAFT => 'Bozza',
        self::STATUS_ACTIVE => 'Attivo',
        self::STATUS_ARCHIVED => 'Archiviato',
    ];

    protected $fillable = [
        'code',
        'type',
        'name',
        'description',
        'status',
        'config',
        'is_system',
    ];

    protected function casts(): array
    {
        return [
            'config' => 'array',
            'is_system' => 'boolean',
        ];
    }

    // ── Relations ─────────────────────────────────────────────────────────────

    public function entitlements(): HasMany
    {
        return $this->hasMany(AgencyEntitlement::class, 'catalog_item_id');
    }

    // ── State helpers ─────────────────────────────────────────────────────────

    public function isActive(): bool
    {
        return $this->status === self::STATUS_ACTIVE;
    }

    // ── Scopes ────────────────────────────────────────────────────────────────

    public function scopeActive($query)
    {
        return $query->where('status', self::STATUS_ACTIVE);
    }
}
