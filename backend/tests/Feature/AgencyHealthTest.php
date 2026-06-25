<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Enums\ActivityLevel;
use App\Enums\PremiumAdoptionLevel;
use App\Enums\TrendDirection;
use App\Enums\UsageLevel;
use App\Models\Central\Agency;
use App\Models\Central\AgencyEntitlement;
use App\Models\Central\PluginCatalogItem;
use App\Models\Central\UsageEvent;
use App\Models\Central\User;
use App\Services\AgencyHealthService;
use Filament\Panel;
use Illuminate\Support\Facades\DB;
use Tests\CentralTestCase;

/**
 * Fase 5B — Agency Health test suite.
 *
 * Tests:
 *  1.  activity HIGH: >= 50 total events
 *  2.  activity MEDIUM: >= 10 and < 50 total events
 *  3.  activity LOW: < 10 total events
 *  4.  design HIGH: >= 10 design events (preview + assigned + fork + layout.saved)
 *  5.  design MEDIUM: >= 3 design events
 *  6.  design LOW: < 3 design events
 *  7.  marketing HIGH: >= 20 premium_block.rendered
 *  8.  marketing LOW: < 5 premium_block.rendered
 *  9.  premium adoption GOOD: has entitlements + premium renders >= threshold
 * 10.  premium adoption PARTIAL: has entitlements but zero premium renders
 * 11.  premium adoption NONE: no active entitlements
 * 12.  trend GROWING: current window > previous by >= 20%
 * 13.  trend DECLINING: current window < previous by >= 20%
 * 14.  trend STABLE: similar event counts both windows
 * 15.  trend STABLE: both windows below min_events threshold
 * 16.  raw numbers in DTO are correct (active_tenants, days_active, counts)
 * 17.  summaryForAllAgencies() returns one DTO per agency
 * 18.  events outside the window are excluded
 * 19.  agency health page only accessible to super admin
 */
class AgencyHealthTest extends CentralTestCase
{
    private static int $seq = 0;

    // ── Helpers ───────────────────────────────────────────────────────────────

    private function makeAgency(): Agency
    {
        self::$seq++;

        return Agency::create([
            'name' => 'Health Agency '.self::$seq,
            'slug' => 'health-agency-'.self::$seq,
            'brand_name' => 'Health Agency '.self::$seq,
            'status' => 'active',
            'billing_type' => 'monthly',
        ]);
    }

    private function makeTenant(Agency $agency): string
    {
        self::$seq++;
        $id = 'health-store-'.self::$seq;

        DB::connection('central')->table('tenants')->insert([
            'id' => $id,
            'name' => 'Health Store '.self::$seq,
            'status' => 'active',
            'agency_id' => $agency->id,
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        return $id;
    }

    private function track(Agency $agency, string $eventType, int $count = 1, ?\DateTime $at = null): void
    {
        for ($i = 0; $i < $count; $i++) {
            UsageEvent::create([
                'agency_id' => $agency->id,
                'event_type' => $eventType,
                'event_group' => UsageEvent::GROUP_PANEL,
                'occurred_at' => $at ?? now(),
            ]);
        }
    }

    private function trackStorefront(Agency $agency, string $tenantId, int $count = 1): void
    {
        for ($i = 0; $i < $count; $i++) {
            UsageEvent::create([
                'agency_id' => $agency->id,
                'tenant_id' => $tenantId,
                'event_type' => UsageEvent::EVENT_STOREFRONT_RENDERED,
                'event_group' => UsageEvent::GROUP_STOREFRONT,
                'occurred_at' => now(),
            ]);
        }
    }

    private function grantEntitlement(Agency $agency): AgencyEntitlement
    {
        $item = PluginCatalogItem::firstOrCreate(
            ['code' => 'block_pack_marketing'],
            ['type' => PluginCatalogItem::TYPE_BLOCK_PACK, 'name' => 'Marketing Block Pack', 'status' => PluginCatalogItem::STATUS_ACTIVE],
        );

        return AgencyEntitlement::create([
            'agency_id' => $agency->id,
            'catalog_item_id' => $item->id,
            'source' => AgencyEntitlement::SOURCE_MANUAL,
            'status' => AgencyEntitlement::STATUS_ACTIVE,
        ]);
    }

    private function svc(): AgencyHealthService
    {
        return app(AgencyHealthService::class);
    }

    private function makeSuperAdmin(): User
    {
        self::$seq++;

        return User::create([
            'name' => 'Super Admin',
            'email' => 'superadmin'.self::$seq.'@example.com',
            'password' => bcrypt('password'),
            'is_super_admin' => true,
        ]);
    }

    private function makeRegularUser(): User
    {
        self::$seq++;

        return User::create([
            'name' => 'Regular User',
            'email' => 'user'.self::$seq.'@example.com',
            'password' => bcrypt('password'),
            'is_super_admin' => false,
        ]);
    }

    private function makePanelStub(string $id): Panel
    {
        $panel = $this->createMock(Panel::class);
        $panel->method('getId')->willReturn($id);

        return $panel;
    }

    // ── 1. Activity HIGH ──────────────────────────────────────────────────────

    public function test_activity_level_is_high_when_50_or_more_events(): void
    {
        $agency = $this->makeAgency();
        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 50);

        $dto = $this->svc()->summaryForAgency($agency);

        $this->assertSame(ActivityLevel::High, $dto->activityLevel);
        $this->assertSame(50, $dto->totalEvents);
    }

    // ── 2. Activity MEDIUM ────────────────────────────────────────────────────

    public function test_activity_level_is_medium_when_10_to_49_events(): void
    {
        $agency = $this->makeAgency();
        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 15);

        $dto = $this->svc()->summaryForAgency($agency);

        $this->assertSame(ActivityLevel::Medium, $dto->activityLevel);
    }

    // ── 3. Activity LOW ───────────────────────────────────────────────────────

    public function test_activity_level_is_low_when_fewer_than_10_events(): void
    {
        $agency = $this->makeAgency();
        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 3);

        $dto = $this->svc()->summaryForAgency($agency);

        $this->assertSame(ActivityLevel::Low, $dto->activityLevel);
    }

    // ── 4. Design HIGH ────────────────────────────────────────────────────────

    public function test_design_usage_is_high_when_10_or_more_design_events(): void
    {
        $agency = $this->makeAgency();
        $this->track($agency, UsageEvent::EVENT_THEME_PREVIEW_OPENED, 4);
        $this->track($agency, UsageEvent::EVENT_THEME_FORK_CREATED, 3);
        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 4);  // total design = 11

        $dto = $this->svc()->summaryForAgency($agency);

        $this->assertSame(UsageLevel::High, $dto->designUsageLevel);
    }

    // ── 5. Design MEDIUM ──────────────────────────────────────────────────────

    public function test_design_usage_is_medium_when_3_to_9_design_events(): void
    {
        $agency = $this->makeAgency();
        $this->track($agency, UsageEvent::EVENT_THEME_PREVIEW_OPENED, 3);

        $dto = $this->svc()->summaryForAgency($agency);

        $this->assertSame(UsageLevel::Medium, $dto->designUsageLevel);
    }

    // ── 6. Design LOW ─────────────────────────────────────────────────────────

    public function test_design_usage_is_low_when_fewer_than_3_design_events(): void
    {
        $agency = $this->makeAgency();
        $this->track($agency, UsageEvent::EVENT_THEME_PREVIEW_OPENED, 1);

        $dto = $this->svc()->summaryForAgency($agency);

        $this->assertSame(UsageLevel::Low, $dto->designUsageLevel);
    }

    // ── 7. Marketing HIGH ─────────────────────────────────────────────────────

    public function test_marketing_usage_is_high_when_20_or_more_premium_block_renders(): void
    {
        $agency = $this->makeAgency();
        $this->track($agency, UsageEvent::EVENT_PREMIUM_BLOCK_RENDERED, 20);

        $dto = $this->svc()->summaryForAgency($agency);

        $this->assertSame(UsageLevel::High, $dto->marketingUsageLevel);
    }

    // ── 8. Marketing LOW ──────────────────────────────────────────────────────

    public function test_marketing_usage_is_low_when_fewer_than_5_premium_block_renders(): void
    {
        $agency = $this->makeAgency();
        $this->track($agency, UsageEvent::EVENT_PREMIUM_BLOCK_RENDERED, 2);

        $dto = $this->svc()->summaryForAgency($agency);

        $this->assertSame(UsageLevel::Low, $dto->marketingUsageLevel);
    }

    // ── 9. Premium adoption GOOD ──────────────────────────────────────────────

    public function test_premium_adoption_is_good_when_entitlements_and_sufficient_renders(): void
    {
        $agency = $this->makeAgency();
        $this->grantEntitlement($agency);
        $this->track($agency, UsageEvent::EVENT_PREMIUM_BLOCK_RENDERED, 5); // equals 'good' threshold

        $dto = $this->svc()->summaryForAgency($agency);

        $this->assertSame(PremiumAdoptionLevel::Good, $dto->premiumAdoptionLevel);
    }

    // ── 10. Premium adoption PARTIAL ──────────────────────────────────────────

    public function test_premium_adoption_is_partial_when_entitlements_but_zero_renders(): void
    {
        $agency = $this->makeAgency();
        $this->grantEntitlement($agency);
        // No premium renders

        $dto = $this->svc()->summaryForAgency($agency);

        $this->assertSame(PremiumAdoptionLevel::Partial, $dto->premiumAdoptionLevel);
    }

    // ── 11. Premium adoption NONE ─────────────────────────────────────────────

    public function test_premium_adoption_is_none_when_no_entitlements(): void
    {
        $agency = $this->makeAgency();
        $this->track($agency, UsageEvent::EVENT_PREMIUM_BLOCK_RENDERED, 10);
        // No entitlements even though renders exist

        $dto = $this->svc()->summaryForAgency($agency);

        $this->assertSame(PremiumAdoptionLevel::None, $dto->premiumAdoptionLevel);
    }

    // ── 12. Trend GROWING ─────────────────────────────────────────────────────

    public function test_trend_is_growing_when_current_window_exceeds_previous_by_20_pct(): void
    {
        $agency = $this->makeAgency();

        // Previous window (31–60 days ago): 10 events
        $oldDate = now()->subDays(45);
        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 10, $oldDate);

        // Current window (last 30 days): 15 events (+50%)
        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 15);

        $dto = $this->svc()->summaryForAgency($agency, 30);

        $this->assertSame(TrendDirection::Growing, $dto->trend);
    }

    // ── 13. Trend DECLINING ───────────────────────────────────────────────────

    public function test_trend_is_declining_when_current_window_drops_by_20_pct(): void
    {
        $agency = $this->makeAgency();

        // Previous window: 15 events
        $oldDate = now()->subDays(45);
        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 15, $oldDate);

        // Current window: 10 events (−33%)
        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 10);

        $dto = $this->svc()->summaryForAgency($agency, 30);

        $this->assertSame(TrendDirection::Declining, $dto->trend);
    }

    // ── 14. Trend STABLE ──────────────────────────────────────────────────────

    public function test_trend_is_stable_when_change_is_within_threshold(): void
    {
        $agency = $this->makeAgency();

        $oldDate = now()->subDays(45);
        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 10, $oldDate);
        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 11); // +10%, within ±20%

        $dto = $this->svc()->summaryForAgency($agency, 30);

        $this->assertSame(TrendDirection::Stable, $dto->trend);
    }

    // ── 15. Trend STABLE when below min_events ────────────────────────────────

    public function test_trend_is_stable_when_both_windows_below_min_events(): void
    {
        $agency = $this->makeAgency();
        // 3 events in each window — below min_events=5
        $this->track($agency, UsageEvent::EVENT_THEME_PREVIEW_OPENED, 3, now()->subDays(45));
        $this->track($agency, UsageEvent::EVENT_THEME_PREVIEW_OPENED, 1);

        $dto = $this->svc()->summaryForAgency($agency, 30);

        $this->assertSame(TrendDirection::Stable, $dto->trend);
    }

    // ── 16. Raw numbers are correct ───────────────────────────────────────────

    public function test_dto_contains_correct_raw_counts(): void
    {
        $agency = $this->makeAgency();
        $storeA = $this->makeTenant($agency);
        $storeB = $this->makeTenant($agency);

        $this->track($agency, UsageEvent::EVENT_THEME_PREVIEW_OPENED, 3);
        $this->track($agency, UsageEvent::EVENT_THEME_FORK_CREATED, 2);
        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 4);
        $this->track($agency, UsageEvent::EVENT_PREMIUM_BLOCK_RENDERED, 7);
        $this->trackStorefront($agency, $storeA, 5);
        $this->trackStorefront($agency, $storeB, 3);

        $dto = $this->svc()->summaryForAgency($agency, 30);

        $this->assertSame(3, $dto->previewCount);
        $this->assertSame(2, $dto->forkCount);
        $this->assertSame(4, $dto->layoutSavedCount);
        $this->assertSame(7, $dto->premiumBlockRenders);
        $this->assertSame(2, $dto->activeTenants); // 2 distinct stores
        $this->assertSame(24, $dto->totalEvents);  // 3+2+4+7+5+3
        $this->assertGreaterThan(0, $dto->daysActive);
    }

    // ── 17. summaryForAllAgencies() ───────────────────────────────────────────

    public function test_summary_for_all_agencies_returns_one_dto_per_agency(): void
    {
        $agencyA = $this->makeAgency();
        $agencyB = $this->makeAgency();
        $agencyC = $this->makeAgency();

        $this->track($agencyA, UsageEvent::EVENT_LAYOUT_SAVED, 5);
        $this->track($agencyB, UsageEvent::EVENT_LAYOUT_SAVED, 20);

        $all = $this->svc()->summaryForAllAgencies();

        $ids = $all->pluck('agencyId')->sort()->values()->all();

        $this->assertContains($agencyA->id, $ids);
        $this->assertContains($agencyB->id, $ids);
        $this->assertContains($agencyC->id, $ids);

        // C had no events — should still appear with LOW activity
        $dtoC = $all->firstWhere('agencyId', $agencyC->id);
        $this->assertSame(ActivityLevel::Low, $dtoC->activityLevel);
        $this->assertSame(0, $dtoC->totalEvents);
    }

    // ── 18. Events outside window are excluded ────────────────────────────────

    public function test_events_outside_window_are_not_counted(): void
    {
        $agency = $this->makeAgency();

        // Old events, outside 30-day window
        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 40, now()->subDays(45));
        // Recent events inside window
        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 5);

        $dto = $this->svc()->summaryForAgency($agency, 30);

        $this->assertSame(5, $dto->totalEvents);
        $this->assertSame(ActivityLevel::Low, $dto->activityLevel); // 5 < medium threshold of 10
    }

    // ── 19. Authorization ─────────────────────────────────────────────────────

    public function test_agency_health_page_only_accessible_to_super_admin(): void
    {
        $superAdmin = $this->makeSuperAdmin();
        $regularUser = $this->makeRegularUser();

        $adminPanel = $this->makePanelStub('admin');

        $this->assertTrue($superAdmin->canAccessPanel($adminPanel));
        $this->assertFalse($regularUser->canAccessPanel($adminPanel));
    }
}
