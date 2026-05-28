<?php

declare(strict_types=1);

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Agency extends Model
{
    use HasFactory;

    protected $connection = 'central';

    protected $fillable = [
        'name',
        'slug',
        'domain',
        'custom_domain',
        'logo_url',
        'favicon_url',
        'primary_color',
        'brand_name',
        'support_email',
        'support_url',
        'stripe_connect_account_id',
        'stripe_connect_onboarded',
        'owner_user_id',
        'plan_id',
        'billing_type',
        'ltdcode',
        'status',
        'hide_linkbay_branding',
    ];

    protected $casts = [
        'hide_linkbay_branding' => 'boolean',
        'stripe_connect_onboarded' => 'boolean',
    ];

    // ── Relations ─────────────────────────────────────────────────────────────

    public function tenants()
    {
        return $this->hasMany(Tenant::class);
    }

    public function plan()
    {
        return $this->belongsTo(Plan::class);
    }

    public function owner()
    {
        return $this->belongsTo(User::class, 'owner_user_id');
    }

    public function creditLedger()
    {
        return $this->hasMany(AiCreditLedger::class);
    }

    // ── Scopes ─────────────────────────────────────────────────────────────────

    public function scopeActive($query)
    {
        return $query->where('status', 'active');
    }

    // ── Accessors ──────────────────────────────────────────────────────────────

    public function creditBalance(): int
    {
        return (int) $this->creditLedger()->sum('amount');
    }

    public function resolvedPrimaryColor(): string
    {
        $color = $this->primary_color ?? '#f59e0b';
        return str_starts_with($color, '#') ? $color : '#f59e0b';
    }

    public function panelDomain(): string
    {
        return $this->custom_domain
            ?? $this->domain
            ?? ($this->slug . '.' . config('tenancy.central_domains.2', 'linkbay-cms.com'));
    }

    public function canUseFeature(string $feature): bool
    {
        $limits = $this->plan?->limits ?? [];
        $value = $limits[$feature] ?? false;

        if (is_bool($value)) {
            return $value;
        }

        if (is_numeric($value)) {
            return $value > 0;
        }

        return (bool) $value;
    }

    public function transactionFeePct(): float
    {
        return (float) ($this->plan?->limits['transaction_fee_pct'] ?? 2.5);
    }

    // ── Static helpers ─────────────────────────────────────────────────────────

    public static function fromDomain(string $domain): ?self
    {
        return static::where('custom_domain', $domain)
            ->orWhere('domain', $domain)
            ->orWhere('slug', explode('.', $domain)[0])
            ->first();
    }
}
