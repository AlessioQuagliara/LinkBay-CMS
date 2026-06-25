<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Central\Agency;
use App\Models\Central\AgencyEntitlement;
use Illuminate\Support\Collection;

/**
 * Single entry-point for all feature access checks.
 *
 * Priority order (first match wins):
 *  1. Plan-based access  → Agency::canUseFeature() checks plan->limits / plan->features
 *  2. Active entitlement → AgencyEntitlement with status=active and valid date window
 *  3. Legacy grant       → LEGACY_FEATURE_GRANTS maps old codes to new ones (backward compat)
 *
 * Callers should prefer this service over Agency::canUseFeature() directly
 * so that entitlement-granted access is included automatically.
 */
class FeatureAccessService
{
    /**
     * Agencies holding a legacy feature code gain access to all codes it maps to.
     * Used for backward compatibility after Fase 4C SKU separation (theme_premium → per-pack codes).
     */
    private const LEGACY_FEATURE_GRANTS = [
        'theme_premium' => ['theme_pack_editorial', 'theme_pack_business'],
    ];

    /** @var array<string, bool> Keyed "agencyId:code" — avoids repeated DB hits within one request. */
    private array $accessCache = [];

    /**
     * Return true if the agency may use the given feature code,
     * either through their plan, an active entitlement, or a legacy grant.
     */
    public function canUseFeature(Agency $agency, string $code): bool
    {
        $key = $agency->id.':'.$code;

        if (array_key_exists($key, $this->accessCache)) {
            return $this->accessCache[$key];
        }

        return $this->accessCache[$key] = $this->resolveAccess($agency, $code);
    }

    private function resolveAccess(Agency $agency, string $code): bool
    {
        if ($agency->canUseFeature($code) || $this->hasActiveEntitlement($agency, $code)) {
            return true;
        }

        // Check whether any legacy code held by the agency grants access to this code.
        foreach (self::LEGACY_FEATURE_GRANTS as $legacyCode => $grantedCodes) {
            if (in_array($code, $grantedCodes, true)) {
                if ($agency->canUseFeature($legacyCode) || $this->hasActiveEntitlement($agency, $legacyCode)) {
                    return true;
                }
            }
        }

        return false;
    }

    /**
     * Return true if the agency has an active, non-expired entitlement
     * for the catalog item with the given code — plan is NOT checked.
     */
    public function hasActiveEntitlement(Agency $agency, string $code): bool
    {
        return AgencyEntitlement::query()
            ->forAgency($agency->id)
            ->active()
            ->whereHas('catalogItem', fn ($q) => $q->where('code', $code))
            ->exists();
    }

    /**
     * Return all feature codes accessible to the agency (plan + entitlements).
     *
     * @return Collection<int, string>
     */
    public function grantedFeatures(Agency $agency): Collection
    {
        // Mirror Agency::canUseFeature(): features are keys in plan->limits with truthy values.
        $planFeatures = collect($agency->plan?->limits ?? [])->filter()->keys();

        $entitlementFeatures = AgencyEntitlement::query()
            ->forAgency($agency->id)
            ->active()
            ->with('catalogItem')
            ->get()
            ->pluck('catalogItem.code')
            ->filter();

        return $planFeatures->merge($entitlementFeatures)->unique()->values();
    }

    /**
     * Return a human-readable reason why access is denied, or null if access is granted.
     */
    public function explainDenied(Agency $agency, string $code): ?string
    {
        if ($this->canUseFeature($agency, $code)) {
            return null;
        }

        $hasRevoked = AgencyEntitlement::query()
            ->forAgency($agency->id)
            ->where('status', AgencyEntitlement::STATUS_REVOKED)
            ->whereHas('catalogItem', fn ($q) => $q->where('code', $code))
            ->exists();

        if ($hasRevoked) {
            return 'Entitlement revocato.';
        }

        $hasExpired = AgencyEntitlement::query()
            ->forAgency($agency->id)
            ->where('status', AgencyEntitlement::STATUS_EXPIRED)
            ->whereHas('catalogItem', fn ($q) => $q->where('code', $code))
            ->exists();

        if ($hasExpired) {
            return 'Entitlement scaduto.';
        }

        // Check if there's a time-windowed active entitlement that hasn't started yet
        $pending = AgencyEntitlement::query()
            ->forAgency($agency->id)
            ->where('status', AgencyEntitlement::STATUS_ACTIVE)
            ->whereNotNull('starts_at')
            ->where('starts_at', '>', now())
            ->whereHas('catalogItem', fn ($q) => $q->where('code', $code))
            ->exists();

        if ($pending) {
            return 'Entitlement non ancora attivo.';
        }

        return 'Feature non inclusa nel piano e nessun entitlement attivo.';
    }
}
