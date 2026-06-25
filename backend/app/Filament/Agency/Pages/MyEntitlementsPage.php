<?php

declare(strict_types=1);

namespace App\Filament\Agency\Pages;

use App\Filament\Agency\Concerns\ResolvesCurrentAgency;
use App\Models\Central\AgencyEntitlement;
use App\Models\Central\Plan;
use App\Models\Central\UsageEvent;
use App\Services\PremiumPackConfig;
use App\Services\UsageEventService;
use Filament\Pages\Page;
use Illuminate\Support\Collection;

class MyEntitlementsPage extends Page
{
    use ResolvesCurrentAgency;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-puzzle-piece';

    protected static ?string $navigationLabel = 'I miei entitlements';

    protected static ?string $slug = 'my-entitlements';

    protected string $view = 'filament.agency.pages.my-entitlements';

    public static function canAccess(): bool
    {
        $member = static::currentMemberStatic();

        return $member?->isOwnerOrAdmin() ?? false;
    }

    public function mount(): void
    {
        app(UsageEventService::class)->track(
            eventType: UsageEvent::EVENT_ENTITLEMENT_VIEWED,
            agencyId: $this->agency()?->id,
        );
    }

    // ── Current plan ──────────────────────────────────────────────────────────

    public function currentPlan(): ?Plan
    {
        return $this->agency()?->plan;
    }

    // ── Feature codes granted via plan ────────────────────────────────────────

    /**
     * Returns the feature codes that are enabled via the agency's current plan.
     * Mirrors Agency::canUseFeature(): keys in plan->limits with truthy values.
     *
     * @return array<int, string>
     */
    public function planFeatures(): array
    {
        $limits = $this->agency()?->plan?->limits ?? [];

        return array_values(array_keys(array_filter($limits)));
    }

    // ── Active entitlements (manual/promo/license grants) ─────────────────────

    /**
     * @return Collection<int, AgencyEntitlement>
     */
    public function activeEntitlements(): Collection
    {
        $agency = $this->agency();
        if (! $agency) {
            return collect();
        }

        return AgencyEntitlement::query()
            ->forAgency($agency->id)
            ->active()
            ->with('catalogItem')
            ->orderBy('created_at')
            ->get();
    }

    // ── Inactive entitlements (expired or revoked) ────────────────────────────

    /**
     * @return Collection<int, AgencyEntitlement>
     */
    public function inactiveEntitlements(): Collection
    {
        $agency = $this->agency();
        if (! $agency) {
            return collect();
        }

        return AgencyEntitlement::query()
            ->forAgency($agency->id)
            ->whereIn('status', [AgencyEntitlement::STATUS_EXPIRED, AgencyEntitlement::STATUS_REVOKED])
            ->with('catalogItem')
            ->orderByDesc('updated_at')
            ->get();
    }

    // ── Premium packs not yet active ─────────────────────────────────────────

    /**
     * Returns premium packs the agency does not currently have access to.
     * Used to show discovery / upgrade nudges on the entitlements page.
     *
     * @return array<int, array{featureCode: string, label: string, description: string, type: string, includes: string[], ctaLabel: string}>
     */
    public function unavailablePremiumPacks(): array
    {
        return PremiumPackConfig::unavailableFor($this->agency());
    }

    // ── Summary stats for KPI cards ───────────────────────────────────────────

    /**
     * @return array{active_features: int, premium_addons: int, inactive_count: int}
     */
    public function summaryStats(): array
    {
        $agency = $this->agency();
        if (! $agency) {
            return ['active_features' => 0, 'premium_addons' => 0, 'inactive_count' => 0];
        }

        $planFeatureCount = count(array_filter($agency->plan?->limits ?? []));

        $activeCount = AgencyEntitlement::query()
            ->forAgency($agency->id)
            ->active()
            ->count();

        $inactiveCount = AgencyEntitlement::query()
            ->forAgency($agency->id)
            ->whereIn('status', [AgencyEntitlement::STATUS_EXPIRED, AgencyEntitlement::STATUS_REVOKED])
            ->count();

        return [
            'active_features' => $planFeatureCount + $activeCount,
            'premium_addons' => $activeCount,
            'inactive_count' => $inactiveCount,
        ];
    }
}
