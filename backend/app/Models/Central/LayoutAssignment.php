<?php

declare(strict_types=1);

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class LayoutAssignment extends Model
{
    protected $connection = 'central';

    /** Supported page slot keys. */
    public const PAGE_KEYS = ['home', 'landing', 'about', 'contact', 'custom'];

    protected $fillable = [
        'agency_id',
        'tenant_id',
        'layout_template_id',
        'page_key',
    ];

    // ── Relations ─────────────────────────────────────────────────────────────

    public function agency(): BelongsTo
    {
        return $this->belongsTo(Agency::class);
    }

    public function layoutTemplate(): BelongsTo
    {
        return $this->belongsTo(LayoutTemplate::class);
    }

    public function tenant(): BelongsTo
    {
        return $this->belongsTo(Tenant::class);
    }
}
