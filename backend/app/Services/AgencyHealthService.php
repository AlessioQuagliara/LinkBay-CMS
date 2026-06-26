<?php

declare(strict_types=1);

namespace App\Services;

use App\Enums\ActivityLevel;
use App\Enums\PremiumAdoptionLevel;
use App\Enums\TrendDirection;
use App\Enums\UsageLevel;
use App\Models\Central\Agency;
use App\Models\Central\AgencyEntitlement;
use App\Models\Central\UsageEvent;
use App\Services\DTO\AgencyHealthDTO;
use Illuminate\Support\Carbon;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;

/**
 * Computes a multi-signal health snapshot for agencies.
 *
 * All queries are batch-oriented: a single call to summaryForAllAgencies()
 * issues ~8 queries regardless of agency count (no N+1).
 *
 * Classification thresholds live in config/agency_health.php.
 */
class AgencyHealthService
{
    // ── Public API ────────────────────────────────────────────────────────────

    public function summaryForAgency(Agency $agency, int $days = 30): AgencyHealthDTO
    {
        [$windowStart, $windowEnd, $prevStart, $prevEnd] = $this->windows($days);

        $ids = [$agency->id];

        return $this->buildDTO(
            agency: $agency,
            days: $days,
            counts: $this->batchEventCounts($ids, $windowStart, $windowEnd)[$agency->id] ?? [],
            prevCounts: $this->batchEventCounts($ids, $prevStart, $prevEnd)[$agency->id] ?? [],
            activeTenants: $this->batchActiveTenants($ids, $windowStart, $windowEnd)[$agency->id] ?? 0,
            daysActive: $this->batchDaysActive($ids, $windowStart, $windowEnd)[$agency->id] ?? 0,
            entitlementCount: $this->batchEntitlementCounts($ids)[$agency->id] ?? 0,
        );
    }

    /**
     * Health summary for all agencies in a single batch.
     *
     * @return Collection<int, AgencyHealthDTO>
     */
    public function summaryForAllAgencies(int $days = 30): Collection
    {
        $agencies = Agency::select(['id', 'name'])->get();

        if ($agencies->isEmpty()) {
            return collect();
        }

        [$windowStart, $windowEnd, $prevStart, $prevEnd] = $this->windows($days);

        $ids = $agencies->pluck('id')->all();

        $counts = $this->batchEventCounts($ids, $windowStart, $windowEnd);
        $prevCounts = $this->batchEventCounts($ids, $prevStart, $prevEnd);
        $activeTenantMap = $this->batchActiveTenants($ids, $windowStart, $windowEnd);
        $daysActiveMap = $this->batchDaysActive($ids, $windowStart, $windowEnd);
        $entitlementMap = $this->batchEntitlementCounts($ids);

        return $agencies->map(fn (Agency $agency) => $this->buildDTO(
            agency: $agency,
            days: $days,
            counts: $counts[$agency->id] ?? [],
            prevCounts: $prevCounts[$agency->id] ?? [],
            activeTenants: $activeTenantMap[$agency->id] ?? 0,
            daysActive: $daysActiveMap[$agency->id] ?? 0,
            entitlementCount: $entitlementMap[$agency->id] ?? 0,
        ));
    }

    // ── Batch queries ─────────────────────────────────────────────────────────

    /**
     * Returns [agencyId => [eventType => count]] for the given window.
     *
     * @param  int[]  $agencyIds
     * @return array<int, array<string, int>>
     */
    private function batchEventCounts(array $agencyIds, Carbon $from, Carbon $to): array
    {
        if (empty($agencyIds)) {
            return [];
        }

        $rows = UsageEvent::query()
            ->select(['agency_id', 'event_type', DB::raw('COUNT(*) as count')])
            ->whereIn('agency_id', $agencyIds)
            ->whereBetween('occurred_at', [$from, $to])
            ->groupBy(['agency_id', 'event_type'])
            ->get();

        $result = [];

        foreach ($rows as $row) {
            $result[$row->agency_id][$row->event_type] = (int) $row->count;
        }

        return $result;
    }

    /**
     * Returns [agencyId => distinct active tenant count] for storefront.rendered events.
     *
     * @param  int[]  $agencyIds
     * @return array<int, int>
     */
    private function batchActiveTenants(array $agencyIds, Carbon $from, Carbon $to): array
    {
        if (empty($agencyIds)) {
            return [];
        }

        return UsageEvent::query()
            ->select(['agency_id', DB::raw('COUNT(DISTINCT tenant_id) as count')])
            ->where('event_type', UsageEvent::EVENT_STOREFRONT_RENDERED)
            ->whereIn('agency_id', $agencyIds)
            ->whereBetween('occurred_at', [$from, $to])
            ->groupBy('agency_id')
            ->get()
            ->pluck('count', 'agency_id')
            ->map(fn ($c) => (int) $c)
            ->all();
    }

    /**
     * Returns [agencyId => distinct days with any event].
     *
     * @param  int[]  $agencyIds
     * @return array<int, int>
     */
    private function batchDaysActive(array $agencyIds, Carbon $from, Carbon $to): array
    {
        if (empty($agencyIds)) {
            return [];
        }

        return UsageEvent::query()
            ->select(['agency_id', DB::raw('COUNT(DISTINCT DATE(occurred_at)) as count')])
            ->whereIn('agency_id', $agencyIds)
            ->whereBetween('occurred_at', [$from, $to])
            ->groupBy('agency_id')
            ->get()
            ->pluck('count', 'agency_id')
            ->map(fn ($c) => (int) $c)
            ->all();
    }

    /**
     * Returns [agencyId => active entitlement count] (date-window aware).
     *
     * @param  int[]  $agencyIds
     * @return array<int, int>
     */
    private function batchEntitlementCounts(array $agencyIds): array
    {
        if (empty($agencyIds)) {
            return [];
        }

        return AgencyEntitlement::query()
            ->select(['agency_id', DB::raw('COUNT(*) as count')])
            ->whereIn('agency_id', $agencyIds)
            ->where('status', AgencyEntitlement::STATUS_ACTIVE)
            ->where(fn ($q) => $q->whereNull('starts_at')->orWhere('starts_at', '<=', now()))
            ->where(fn ($q) => $q->whereNull('ends_at')->orWhere('ends_at', '>', now()))
            ->groupBy('agency_id')
            ->get()
            ->pluck('count', 'agency_id')
            ->map(fn ($c) => (int) $c)
            ->all();
    }

    // ── DTO builder ───────────────────────────────────────────────────────────

    /**
     * @param  array<string, int>  $counts  event_type => count, current window
     * @param  array<string, int>  $prevCounts  event_type => count, previous window
     */
    private function buildDTO(
        Agency $agency,
        int $days,
        array $counts,
        array $prevCounts,
        int $activeTenants,
        int $daysActive,
        int $entitlementCount,
    ): AgencyHealthDTO {
        $totalEvents = (int) array_sum($counts);
        $prevTotalEvents = (int) array_sum($prevCounts);

        $previewCount = $counts[UsageEvent::EVENT_THEME_PREVIEW_OPENED] ?? 0;
        $themeAssignedCount = $counts[UsageEvent::EVENT_THEME_ASSIGNED] ?? 0;
        $forkCount = $counts[UsageEvent::EVENT_THEME_FORK_CREATED] ?? 0;
        $layoutSavedCount = $counts[UsageEvent::EVENT_LAYOUT_SAVED] ?? 0;
        $premiumBlockRenders = $counts[UsageEvent::EVENT_PREMIUM_BLOCK_RENDERED] ?? 0;
        $premiumThemeRenders = $counts[UsageEvent::EVENT_THEME_RENDERED] ?? 0;

        $designTotal = $previewCount + $themeAssignedCount + $forkCount + $layoutSavedCount;

        return new AgencyHealthDTO(
            agencyId: $agency->id,
            agencyName: $agency->name,
            windowDays: $days,
            activityLevel: $this->computeActivityLevel($totalEvents),
            designUsageLevel: $this->computeUsageLevel($designTotal, 'design_usage'),
            marketingUsageLevel: $this->computeUsageLevel($premiumBlockRenders, 'marketing_usage'),
            premiumAdoptionLevel: $this->computePremiumAdoption($entitlementCount, $premiumBlockRenders + $premiumThemeRenders),
            trend: $this->computeTrend($totalEvents, $prevTotalEvents),
            totalEvents: $totalEvents,
            activeTenants: $activeTenants,
            daysActive: $daysActive,
            previewCount: $previewCount,
            themeAssignedCount: $themeAssignedCount,
            forkCount: $forkCount,
            layoutSavedCount: $layoutSavedCount,
            premiumBlockRenders: $premiumBlockRenders,
            premiumThemeRenders: $premiumThemeRenders,
            activeEntitlementCount: $entitlementCount,
        );
    }

    // ── Classifiers ───────────────────────────────────────────────────────────

    private function computeActivityLevel(int $total): ActivityLevel
    {
        $t = config('agency_health.activity');

        if ($total >= $t['high']) {
            return ActivityLevel::High;
        }

        if ($total >= $t['medium']) {
            return ActivityLevel::Medium;
        }

        return ActivityLevel::Low;
    }

    private function computeUsageLevel(int $count, string $configKey): UsageLevel
    {
        $t = config("agency_health.{$configKey}");

        if ($count >= $t['high']) {
            return UsageLevel::High;
        }

        if ($count >= $t['medium']) {
            return UsageLevel::Medium;
        }

        return UsageLevel::Low;
    }

    private function computePremiumAdoption(int $entitlementCount, int $premiumRenders): PremiumAdoptionLevel
    {
        if ($entitlementCount === 0) {
            return PremiumAdoptionLevel::None;
        }

        if ($premiumRenders >= config('agency_health.premium_adoption.good')) {
            return PremiumAdoptionLevel::Good;
        }

        return PremiumAdoptionLevel::Partial;
    }

    private function computeTrend(int $current, int $previous): TrendDirection
    {
        $cfg = config('agency_health.trend');

        if ($current < $cfg['min_events'] && $previous < $cfg['min_events']) {
            return TrendDirection::Stable;
        }

        if ($previous === 0) {
            return $current > 0 ? TrendDirection::Growing : TrendDirection::Stable;
        }

        $pct = (($current - $previous) / $previous) * 100;

        if ($pct >= $cfg['growth_pct']) {
            return TrendDirection::Growing;
        }

        if ($pct <= -$cfg['decline_pct']) {
            return TrendDirection::Declining;
        }

        return TrendDirection::Stable;
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    /**
     * Returns [windowStart, windowEnd, prevWindowStart, prevWindowEnd].
     *
     * @return array{Carbon, Carbon, Carbon, Carbon}
     */
    private function windows(int $days): array
    {
        $windowEnd = now();
        $windowStart = now()->subDays($days)->startOfDay();
        $prevEnd = $windowStart->copy();
        $prevStart = $windowStart->copy()->subDays($days)->startOfDay();

        return [$windowStart, $windowEnd, $prevStart, $prevEnd];
    }
}
