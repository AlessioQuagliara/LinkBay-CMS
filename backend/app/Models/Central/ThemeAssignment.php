<?php

declare(strict_types=1);

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class ThemeAssignment extends Model
{
    protected $connection = 'central';

    protected $fillable = [
        'agency_id',
        'tenant_id',
        'theme_preset_id',
    ];

    // ── Relations ─────────────────────────────────────────────────────────────

    public function agency(): BelongsTo
    {
        return $this->belongsTo(Agency::class);
    }

    public function tenant(): BelongsTo
    {
        return $this->belongsTo(Tenant::class);
    }

    public function themePreset(): BelongsTo
    {
        return $this->belongsTo(ThemePreset::class);
    }
}
