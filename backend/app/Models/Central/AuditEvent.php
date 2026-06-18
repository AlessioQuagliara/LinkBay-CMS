<?php

declare(strict_types=1);

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

/**
 * Append-only audit log. Never update or soft-delete these records.
 */
class AuditEvent extends Model
{
    protected $connection = 'central';

    public const UPDATED_AT = null;

    // ── Event constants ────────────────────────────────────────────────────────

    public const EVENT_MEMBER_INVITED = 'agency_member.invited';

    public const EVENT_MEMBER_ACCEPTED = 'agency_member.accepted';

    public const EVENT_MEMBER_ROLE_CHANGED = 'agency_member.role_changed';

    public const EVENT_MEMBER_SUSPENDED = 'agency_member.suspended';

    public const EVENT_MEMBER_REACTIVATED = 'agency_member.reactivated';

    public const EVENT_MEMBER_REMOVED = 'agency_member.removed';

    public const EVENT_CLIENT_CREATED = 'agency_client.created';

    public const EVENT_CLIENT_UPDATED = 'agency_client.updated';

    public const EVENT_CLIENT_CONTACT_INVITED = 'agency_client_contact.invited_to_store';

    public const EVENT_STORE_CREATED = 'store.created';

    public const EVENT_STORE_UPDATED = 'store.updated';

    public const EVENT_STORE_PROVISIONED = 'store.provisioned';

    public const EVENT_TERMS_ACCEPTED = 'terms.accepted';

    public const EVENT_BILLING_PORTAL_ACCESSED = 'billing.portal_accessed';

    public const EVENT_LAYOUT_CREATED = 'layout.created';

    public const EVENT_LAYOUT_UPDATED = 'layout.updated';

    public const EVENT_LAYOUT_PUBLISHED = 'layout.published';

    public const EVENT_LAYOUT_DUPLICATED = 'layout.duplicated';

    public const EVENT_LAYOUT_ASSIGNED = 'layout.assigned';

    public const EVENT_THEME_CREATED = 'theme.created';

    public const EVENT_THEME_UPDATED = 'theme.updated';

    public const EVENT_THEME_ACTIVATED = 'theme.activated';

    public const EVENT_THEME_DUPLICATED = 'theme.duplicated';

    public const EVENT_THEME_ASSIGNED = 'theme.assigned';

    /** All known event types, keyed by constant value, value = human label. */
    public const EVENT_LABELS = [
        self::EVENT_MEMBER_INVITED => 'Membro invitato',
        self::EVENT_MEMBER_ACCEPTED => 'Invito accettato',
        self::EVENT_MEMBER_ROLE_CHANGED => 'Ruolo modificato',
        self::EVENT_MEMBER_SUSPENDED => 'Membro sospeso',
        self::EVENT_MEMBER_REACTIVATED => 'Membro riattivato',
        self::EVENT_MEMBER_REMOVED => 'Membro rimosso',
        self::EVENT_CLIENT_CREATED => 'Cliente creato',
        self::EVENT_CLIENT_UPDATED => 'Cliente aggiornato',
        self::EVENT_CLIENT_CONTACT_INVITED => 'Contatto invitato allo store',
        self::EVENT_STORE_CREATED => 'Store creato',
        self::EVENT_STORE_UPDATED => 'Store aggiornato',
        self::EVENT_STORE_PROVISIONED => 'Store provisionato',
        self::EVENT_TERMS_ACCEPTED => 'T&C accettati',
        self::EVENT_BILLING_PORTAL_ACCESSED => 'Portale Stripe aperto',
        self::EVENT_LAYOUT_CREATED => 'Layout template creato',
        self::EVENT_LAYOUT_UPDATED => 'Layout template aggiornato',
        self::EVENT_LAYOUT_PUBLISHED => 'Layout template pubblicato/bozza',
        self::EVENT_LAYOUT_DUPLICATED => 'Layout template duplicato',
        self::EVENT_LAYOUT_ASSIGNED => 'Layout template assegnato a store',
        self::EVENT_THEME_CREATED => 'Tema creato',
        self::EVENT_THEME_UPDATED => 'Tema aggiornato',
        self::EVENT_THEME_ACTIVATED => 'Tema attivato/disattivato',
        self::EVENT_THEME_DUPLICATED => 'Tema duplicato',
        self::EVENT_THEME_ASSIGNED => 'Tema assegnato a store',
    ];

    protected $fillable = [
        'agency_id',
        'user_id',
        'event',
        'subject_type',
        'subject_id',
        'old_values',
        'new_values',
        'ip_address',
        'metadata',
    ];

    protected function casts(): array
    {
        return [
            'old_values' => 'array',
            'new_values' => 'array',
            'metadata' => 'array',
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

    // ── Helpers ───────────────────────────────────────────────────────────────

    public function eventLabel(): string
    {
        return self::EVENT_LABELS[$this->event] ?? $this->event;
    }

    public function actorLabel(): string
    {
        return $this->user?->name ?? $this->user?->email ?? '—';
    }

    public function subjectLabel(): string
    {
        if ($this->subject_type === null) {
            return '—';
        }

        $type = match ($this->subject_type) {
            'agency_member' => 'Membro',
            'agency_client' => 'Cliente',
            'agency_client_contact' => 'Contatto',
            'store' => 'Store',
            default => $this->subject_type,
        };

        return $this->subject_id ? "{$type} #{$this->subject_id}" : $type;
    }

    public function severityColor(): string
    {
        return match (true) {
            str_contains($this->event, 'removed'),
            str_contains($this->event, 'suspended') => 'danger',
            str_contains($this->event, 'role_changed'),
            str_contains($this->event, 'updated') => 'warning',
            default => 'success',
        };
    }
}
