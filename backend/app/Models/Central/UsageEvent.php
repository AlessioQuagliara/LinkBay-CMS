<?php

declare(strict_types=1);

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

/**
 * Append-only usage event log. Never update or soft-delete these records.
 */
class UsageEvent extends Model
{
    protected $connection = 'central';

    public const UPDATED_AT = null;

    // ── Event types ────────────────────────────────────────────────────────────

    // Panel / agency
    public const EVENT_THEME_PREVIEW_OPENED = 'theme.preview_opened';

    public const EVENT_THEME_ASSIGNED = 'theme.assigned';

    public const EVENT_THEME_FORK_CREATED = 'theme.fork_created';

    public const EVENT_LAYOUT_SAVED = 'layout.saved';

    public const EVENT_ENTITLEMENT_VIEWED = 'entitlement.viewed';

    public const EVENT_BILLING_PORTAL_OPENED = 'billing.portal_opened';

    public const EVENT_TEAM_MEMBER_INVITED = 'team.member_invited';

    // Storefront
    public const EVENT_STOREFRONT_RENDERED = 'storefront.rendered';

    public const EVENT_PREMIUM_BLOCK_RENDERED = 'premium_block.rendered';

    public const EVENT_THEME_RENDERED = 'theme.rendered';

    // ── Groups ────────────────────────────────────────────────────────────────

    public const GROUP_PANEL = 'panel';

    public const GROUP_STOREFRONT = 'storefront';

    // ── Schema ────────────────────────────────────────────────────────────────

    protected $fillable = [
        'agency_id',
        'tenant_id',
        'user_id',
        'event_type',
        'event_group',
        'subject_type',
        'subject_id',
        'meta',
        'occurred_at',
    ];

    protected function casts(): array
    {
        return [
            'meta' => 'array',
            'occurred_at' => 'datetime',
            'created_at' => 'datetime',
        ];
    }

    // ── Relations ─────────────────────────────────────────────────────────────

    public function agency(): BelongsTo
    {
        return $this->belongsTo(Agency::class);
    }

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }
}
