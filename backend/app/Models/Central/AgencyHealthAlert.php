<?php

declare(strict_types=1);

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class AgencyHealthAlert extends Model
{
    protected $connection = 'central';

    protected $fillable = [
        'agency_id',
        'type',
        'severity',
        'detected_at',
        'resolved_at',
        'meta',
    ];

    protected function casts(): array
    {
        return [
            'detected_at' => 'datetime',
            'resolved_at' => 'datetime',
            'meta' => 'array',
        ];
    }

    // ── Type constants ────────────────────────────────────────────────────────

    public const TYPE_LOW_ACTIVITY = 'low_activity';

    public const TYPE_PREMIUM_NOT_USED = 'premium_not_used';

    public const TYPE_DESIGN_DROP = 'design_drop';

    public const TYPE_MARKETING_PACK_INACTIVE = 'marketing_pack_inactive';

    public const TYPES = [
        self::TYPE_LOW_ACTIVITY => 'Attività bassa',
        self::TYPE_PREMIUM_NOT_USED => 'Premium non usato',
        self::TYPE_DESIGN_DROP => 'Design in calo',
        self::TYPE_MARKETING_PACK_INACTIVE => 'Marketing Pack inattivo',
    ];

    // ── Severity constants ────────────────────────────────────────────────────

    public const SEVERITY_LOW = 'low';

    public const SEVERITY_MEDIUM = 'medium';

    public const SEVERITY_HIGH = 'high';

    public const SEVERITIES = [
        self::SEVERITY_LOW => 'Bassa',
        self::SEVERITY_MEDIUM => 'Media',
        self::SEVERITY_HIGH => 'Alta',
    ];

    // ── Relations ─────────────────────────────────────────────────────────────

    public function agency(): BelongsTo
    {
        return $this->belongsTo(Agency::class);
    }

    // ── Scopes ────────────────────────────────────────────────────────────────

    public function scopeOpen($query)
    {
        return $query->whereNull('resolved_at');
    }

    public function scopeResolved($query)
    {
        return $query->whereNotNull('resolved_at');
    }

    public function scopeForAgency($query, int $agencyId)
    {
        return $query->where('agency_id', $agencyId);
    }

    // ── State ─────────────────────────────────────────────────────────────────

    public function isOpen(): bool
    {
        return $this->resolved_at === null;
    }

    public function resolve(): void
    {
        $this->update(['resolved_at' => now()]);
    }
}
