<?php

declare(strict_types=1);

namespace App\Services;

use App\Enums\ActivityLevel;
use App\Enums\TrendDirection;
use App\Enums\UsageLevel;
use App\Models\Central\AgencyEntitlement;
use App\Models\Central\AgencyHealthAlert;
use App\Models\Central\PluginCatalogItem;
use App\Services\DTO\AgencyHealthDTO;

/**
 * Evaluates health rules against all agencies and creates alert records.
 *
 * Each rule maps to a single alert type. Duplicate open alerts of the same
 * type are suppressed — only one open alert per (agency, type) pair is stored.
 *
 * All thresholds and per-rule toggles live in config/agency_alerts.php.
 * Health signals come from AgencyHealthService — no health logic here.
 */
class AgencyAlertService
{
    public function __construct(
        private readonly AgencyHealthService $health,
    ) {}

    /**
     * Run all enabled rules for every agency and persist new alerts.
     *
     * @return array<string, int> type => count of new alerts created
     */
    public function evaluateAndStoreAlerts(int $days = 30): array
    {
        $summaries = $this->health->summaryForAllAgencies($days);

        if ($summaries->isEmpty()) {
            return [];
        }

        $agencyIds = $summaries->pluck('agencyId')->all();
        $marketingPackIds = $this->batchMarketingPackAgencyIds($agencyIds);
        $maturePremiumIds = $this->batchMaturePremiumAgencyIds($agencyIds);
        $openAlerts = $this->batchOpenAlerts($agencyIds);

        $created = [];

        foreach ($summaries as $dto) {
            $types = $this->evaluateRules($dto, $marketingPackIds, $maturePremiumIds);

            foreach ($types as $type) {
                if (in_array($type, $openAlerts[$dto->agencyId] ?? [], true)) {
                    continue;
                }

                $this->createAlert($dto, $type);
                $created[$type] = ($created[$type] ?? 0) + 1;
            }
        }

        return $created;
    }

    // ── Rules ─────────────────────────────────────────────────────────────────

    /**
     * @param  int[]  $marketingPackIds  agency IDs with active marketing pack entitlement
     * @param  int[]  $maturePremiumIds  agency IDs with a mature (>= N days old) premium entitlement
     * @return string[]
     */
    private function evaluateRules(AgencyHealthDTO $dto, array $marketingPackIds, array $maturePremiumIds): array
    {
        $types = [];

        // Rule 1 — Low activity with declining trend
        if (config('agency_alerts.rules.low_activity.enabled', true)) {
            if ($dto->activityLevel === ActivityLevel::Low && $dto->trend === TrendDirection::Declining) {
                $types[] = AgencyHealthAlert::TYPE_LOW_ACTIVITY;
            }
        }

        // Rule 2 — Premium pack active >= N days but literally zero premium renders
        // (PremiumAdoptionLevel::None means no entitlements; Partial means entitlements + < 5 renders.
        //  We specifically want: has entitlement + zero renders ever in the window.)
        if (config('agency_alerts.rules.premium_not_used.enabled', true)) {
            if (
                $dto->activeEntitlementCount > 0
                && ($dto->premiumBlockRenders + $dto->premiumThemeRenders) === 0
                && in_array($dto->agencyId, $maturePremiumIds, true)
            ) {
                $types[] = AgencyHealthAlert::TYPE_PREMIUM_NOT_USED;
            }
        }

        // Rule 3 — Design usage declining (not High now + overall trend declining)
        if (config('agency_alerts.rules.design_drop.enabled', true)) {
            if (
                $dto->trend === TrendDirection::Declining
                && $dto->designUsageLevel !== UsageLevel::High
                && $dto->totalEvents >= config('agency_alerts.min_events_for_design_alert', 5)
            ) {
                $types[] = AgencyHealthAlert::TYPE_DESIGN_DROP;
            }
        }

        // Rule 4 — Marketing Pack active but usage is Low
        if (config('agency_alerts.rules.marketing_pack_inactive.enabled', true)) {
            if (
                in_array($dto->agencyId, $marketingPackIds, true)
                && $dto->marketingUsageLevel === UsageLevel::Low
            ) {
                $types[] = AgencyHealthAlert::TYPE_MARKETING_PACK_INACTIVE;
            }
        }

        return $types;
    }

    // ── Queries ───────────────────────────────────────────────────────────────

    /**
     * Returns agency IDs that have an active block_pack_marketing entitlement.
     *
     * @param  int[]  $agencyIds
     * @return int[]
     */
    private function batchMarketingPackAgencyIds(array $agencyIds): array
    {
        if (empty($agencyIds)) {
            return [];
        }

        $item = PluginCatalogItem::where('code', 'block_pack_marketing')->first();

        if (! $item) {
            return [];
        }

        return AgencyEntitlement::query()
            ->whereIn('agency_id', $agencyIds)
            ->where('catalog_item_id', $item->id)
            ->where('status', AgencyEntitlement::STATUS_ACTIVE)
            ->where(fn ($q) => $q->whereNull('starts_at')->orWhere('starts_at', '<=', now()))
            ->where(fn ($q) => $q->whereNull('ends_at')->orWhere('ends_at', '>', now()))
            ->pluck('agency_id')
            ->all();
    }

    /**
     * Returns agency IDs that have at least one active premium entitlement older than
     * the configured minimum days — used to avoid triggering alerts for fresh subscribers.
     *
     * @param  int[]  $agencyIds
     * @return int[]
     */
    private function batchMaturePremiumAgencyIds(array $agencyIds): array
    {
        if (empty($agencyIds)) {
            return [];
        }

        $minDays = config('agency_alerts.min_days_since_premium', 30);

        return AgencyEntitlement::query()
            ->whereIn('agency_id', $agencyIds)
            ->active()
            ->where('created_at', '<=', now()->subDays($minDays))
            ->distinct()
            ->pluck('agency_id')
            ->all();
    }

    /**
     * Returns [agencyId => string[]] of currently open alert types per agency.
     *
     * @param  int[]  $agencyIds
     * @return array<int, string[]>
     */
    private function batchOpenAlerts(array $agencyIds): array
    {
        if (empty($agencyIds)) {
            return [];
        }

        return AgencyHealthAlert::whereIn('agency_id', $agencyIds)
            ->whereNull('resolved_at')
            ->get(['agency_id', 'type'])
            ->groupBy('agency_id')
            ->map(fn ($group) => $group->pluck('type')->all())
            ->all();
    }

    private function createAlert(AgencyHealthDTO $dto, string $type): AgencyHealthAlert
    {
        return AgencyHealthAlert::create([
            'agency_id' => $dto->agencyId,
            'type' => $type,
            'severity' => config("agency_alerts.severity.{$type}", AgencyHealthAlert::SEVERITY_MEDIUM),
            'detected_at' => now(),
            'meta' => [
                'activity_level' => $dto->activityLevel->value,
                'trend' => $dto->trend->value,
                'total_events' => $dto->totalEvents,
                'days' => $dto->windowDays,
            ],
        ]);
    }
}
