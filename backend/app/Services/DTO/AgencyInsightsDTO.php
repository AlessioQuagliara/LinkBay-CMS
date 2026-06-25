<?php

declare(strict_types=1);

namespace App\Services\DTO;

use App\Enums\TrendDirection;

/**
 * Presentation-oriented snapshot of an agency's activity.
 *
 * Intentionally simpler than AgencyHealthDTO — it exposes only
 * what the agency panel shows to the agency owner/admin.
 * Health scores and internal classifiers stay server-side.
 */
final class AgencyInsightsDTO
{
    public function __construct(
        public readonly int $agencyId,
        public readonly int $windowDays,

        // ── KPIs ─────────────────────────────────────────────────────────────
        public readonly int $activeStoresCount,
        public readonly int $totalStoresCount,
        public readonly int $layoutUpdates,
        public readonly int $marketingBlocksUsed,
        public readonly TrendDirection $trend,

        // ── Per-store activity list ───────────────────────────────────────────
        /** @var array<int, array{id: string, name: string, alive: bool}> */
        public readonly array $storeActivity,

        // ── Premium packs ─────────────────────────────────────────────────────
        /** @var array<int, string> feature codes of active entitlements */
        public readonly array $premiumPackCodes,
        public readonly int $premiumThemeRenders,
        public readonly int $themeForksCreated,

        // ── Conditional UI flags ──────────────────────────────────────────────
        /** Whether the agency has the Marketing Block Pack entitlement. */
        public readonly bool $hasMarketingPack,
        /** Whether the agency has any premium theme pack entitlement. */
        public readonly bool $hasPremiumThemePack,
    ) {}

    /** Stores that had at least one storefront render in the window. */
    public function aliveStores(): array
    {
        return array_filter($this->storeActivity, fn ($s) => $s['alive']);
    }

    /** Stores that had zero storefront renders in the window. */
    public function calmStores(): array
    {
        return array_filter($this->storeActivity, fn ($s) => ! $s['alive']);
    }
}
