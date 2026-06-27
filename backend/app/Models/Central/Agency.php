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
        'stripe_customer_id',
        'stripe_subscription_id',
        'stripe_status',
        'trial_ends_at',
        'subscription_ends_at',
        'payment_method_last4',
        'payment_method_brand',
        'billing_email',
        'billing_name',
        'vat_number',
        'billing_address',
        'terms_accepted_version',
        'max_stores_override',
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
        'trial_ends_at' => 'datetime',
        'subscription_ends_at' => 'datetime',
        'billing_address' => 'array',
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

    public function subscription()
    {
        return $this->hasOne(AgencySubscription::class);
    }

    public function commissions()
    {
        return $this->hasMany(CommissionRecord::class);
    }

    public function billingEvents()
    {
        return $this->hasMany(BillingEvent::class);
    }

    public function invoices()
    {
        return $this->hasMany(AgencyInvoice::class)->orderByDesc('created_at');
    }

    public function hasActiveSubscription(): bool
    {
        return in_array($this->stripe_status, ['active', 'trialing'], true);
    }

    public function paymentMethodLabel(): string
    {
        if (! $this->payment_method_last4) {
            return '—';
        }

        $brand = ucfirst($this->payment_method_brand ?? 'Card');

        return "{$brand} •••• {$this->payment_method_last4}";
    }

    public function termsAcceptances()
    {
        return $this->hasMany(TermsAcceptance::class);
    }

    public function agencyClients()
    {
        return $this->hasMany(AgencyClient::class);
    }

    public function agencyMembers()
    {
        return $this->hasMany(AgencyMember::class);
    }

    public function layoutTemplates()
    {
        return $this->hasMany(LayoutTemplate::class);
    }

    public function themePresets()
    {
        return $this->hasMany(ThemePreset::class);
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
        $color = $this->primary_color ?? '#ff5758';

        return str_starts_with($color, '#') ? $color : '#ff5758';
    }

    public function panelDomain(): string
    {
        // Prefer explicit custom_domain, then legacy domain, then auto-build from slug.
        // Uses config('app.central_domain') so local and prod follow the same env var (CENTRAL_DOMAIN).
        return $this->custom_domain
            ?? $this->domain
            ?? ($this->slug.'.'.config('app.central_domain', 'linkbay-cms.com'));
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
        // Exact custom-domain or legacy domain match.
        $match = static::where('custom_domain', $domain)
            ->orWhere('domain', $domain)
            ->first();

        if ($match) {
            return $match;
        }

        // Subdomain-based slug resolution: only when the host is a direct
        // subdomain of the configured central domain.  Avoids matching an
        // arbitrary first component of attacker-controlled domains.
        $centralDomain = config('app.central_domain', 'linkbay-cms.com');

        if (str_ends_with($domain, '.'.$centralDomain)) {
            // Strip the trailing .central_domain to get the slug segment.
            $slug = substr($domain, 0, strlen($domain) - strlen('.'.$centralDomain));

            // Only accept single-level slugs (no dots).
            if ($slug !== '' && ! str_contains($slug, '.')) {
                return static::where('slug', $slug)->first();
            }
        }

        return null;
    }
}
