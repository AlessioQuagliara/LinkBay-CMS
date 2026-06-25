<?php

declare(strict_types=1);

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class AgencyEntitlement extends Model
{
    protected $connection = 'central';

    public const SOURCE_PLAN = 'plan';

    public const SOURCE_MANUAL = 'manual';

    public const SOURCE_PROMO = 'promo';

    public const SOURCE_LICENSE = 'license';

    public const STATUS_ACTIVE = 'active';

    public const STATUS_EXPIRED = 'expired';

    public const STATUS_REVOKED = 'revoked';

    public const SOURCES = [
        self::SOURCE_PLAN => 'Piano',
        self::SOURCE_MANUAL => 'Manuale',
        self::SOURCE_PROMO => 'Promo',
        self::SOURCE_LICENSE => 'Licenza',
    ];

    public const STATUSES = [
        self::STATUS_ACTIVE => 'Attivo',
        self::STATUS_EXPIRED => 'Scaduto',
        self::STATUS_REVOKED => 'Revocato',
    ];

    protected $fillable = [
        'agency_id',
        'catalog_item_id',
        'source',
        'status',
        'starts_at',
        'ends_at',
        'metadata',
    ];

    protected function casts(): array
    {
        return [
            'metadata' => 'array',
            'starts_at' => 'datetime',
            'ends_at' => 'datetime',
        ];
    }

    // ── Relations ─────────────────────────────────────────────────────────────

    public function agency(): BelongsTo
    {
        return $this->belongsTo(Agency::class);
    }

    public function catalogItem(): BelongsTo
    {
        return $this->belongsTo(PluginCatalogItem::class, 'catalog_item_id');
    }

    // ── State helpers ─────────────────────────────────────────────────────────

    public function isActive(): bool
    {
        if ($this->status !== self::STATUS_ACTIVE) {
            return false;
        }

        if ($this->starts_at !== null && $this->starts_at->isFuture()) {
            return false;
        }

        if ($this->ends_at !== null && $this->ends_at->isPast()) {
            return false;
        }

        return true;
    }

    public function revoke(): void
    {
        $this->update(['status' => self::STATUS_REVOKED]);
    }

    public function expire(): void
    {
        $this->update(['status' => self::STATUS_EXPIRED]);
    }

    // ── Scopes ────────────────────────────────────────────────────────────────

    public function scopeActive($query)
    {
        return $query
            ->where('status', self::STATUS_ACTIVE)
            ->where(fn ($q) => $q->whereNull('starts_at')->orWhere('starts_at', '<=', now()))
            ->where(fn ($q) => $q->whereNull('ends_at')->orWhere('ends_at', '>', now()));
    }

    public function scopeForAgency($query, int $agencyId)
    {
        return $query->where('agency_id', $agencyId);
    }
}
