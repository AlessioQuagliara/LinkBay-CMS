<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Central\Agency;
use App\Models\Central\AgencyEntitlement;
use App\Models\Central\UsageEvent;
use App\Services\DTO\AgencyInsightsDTO;
use Illuminate\Support\Facades\DB;

/**
 * Presentation wrapper around AgencyHealthService for the agency panel.
 *
 * Keeps the internal health/classification model server-side by exposing
 * only the data the agency owner/admin needs: store activity, layout updates,
 * marketing block usage, and premium pack adoption.
 *
 * All heavy lifting (batch queries, trend math) is delegated to AgencyHealthService.
 */
class AgencyInsightsService
{
    public function __construct(
        private readonly AgencyHealthService $health,
    ) {}

    public function forAgency(Agency $agency, int $days = 30): AgencyInsightsDTO
    {
        $healthDto = $this->health->summaryForAgency($agency, $days);
        $premiumCodes = $this->activePremiumPackCodes($agency);
        $storeActivity = $this->buildStoreActivity($agency, $days);

        $hasMarketingPack = in_array('block_pack_marketing', $premiumCodes, true);
        $hasPremiumThemePack = ! empty(array_filter(
            $premiumCodes,
            fn ($code) => str_starts_with($code, 'theme_pack') || $code === 'theme_premium',
        ));

        return new AgencyInsightsDTO(
            agencyId: $agency->id,
            windowDays: $days,
            activeStoresCount: $healthDto->activeTenants,
            totalStoresCount: count($storeActivity),
            layoutUpdates: $healthDto->layoutSavedCount,
            marketingBlocksUsed: $healthDto->premiumBlockRenders,
            trend: $healthDto->trend,
            storeActivity: $storeActivity,
            premiumPackCodes: $premiumCodes,
            premiumThemeRenders: $healthDto->premiumThemeRenders,
            themeForksCreated: $healthDto->forkCount,
            hasMarketingPack: $hasMarketingPack,
            hasPremiumThemePack: $hasPremiumThemePack,
        );
    }

    // ── Private helpers ────────────────────────────────────────────────────────

    /**
     * Per-store activity: each store tagged as "alive" (had storefront renders
     * in the window) or not.
     *
     * @return array<int, array{id: string, name: string, alive: bool}>
     */
    private function buildStoreActivity(Agency $agency, int $days): array
    {
        $tenants = DB::connection('central')
            ->table('tenants')
            ->where('agency_id', $agency->id)
            ->get(['id', 'name']);

        if ($tenants->isEmpty()) {
            return [];
        }

        $aliveIds = UsageEvent::query()
            ->select('tenant_id')
            ->where('event_type', UsageEvent::EVENT_STOREFRONT_RENDERED)
            ->where('agency_id', $agency->id)
            ->where('occurred_at', '>=', now()->subDays($days)->startOfDay())
            ->whereNotNull('tenant_id')
            ->distinct()
            ->pluck('tenant_id')
            ->flip()
            ->all();

        return $tenants->map(fn ($t) => [
            'id' => $t->id,
            'name' => $t->name,
            'alive' => isset($aliveIds[$t->id]),
        ])->values()->all();
    }

    /**
     * Feature codes of active entitlements for the agency.
     *
     * @return array<int, string>
     */
    private function activePremiumPackCodes(Agency $agency): array
    {
        return AgencyEntitlement::forAgency($agency->id)
            ->active()
            ->with('catalogItem')
            ->get()
            ->pluck('catalogItem.code')
            ->filter()
            ->values()
            ->all();
    }
}
