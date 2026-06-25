<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Enums\TrendDirection;
use App\Filament\Agency\Pages\AgencyInsightsPage;
use App\Models\Central\Agency;
use App\Models\Central\AgencyEntitlement;
use App\Models\Central\AgencyMember;
use App\Models\Central\PluginCatalogItem;
use App\Models\Central\UsageEvent;
use App\Models\User;
use App\Services\AgencyInsightsService;
use Illuminate\Support\Facades\DB;
use Tests\CentralTestCase;

/**
 * Fase 5C — Agency Insights test suite.
 *
 * Tests:
 *  1.  activeStoresCount reflects tenants that had storefront renders
 *  2.  totalStoresCount includes all tenants regardless of activity
 *  3.  stores without renders have alive = false
 *  4.  layoutUpdates reflects layout.saved count in the window
 *  5.  marketingBlocksUsed reflects premium_block.rendered count
 *  6.  hasMarketingPack is true when block_pack_marketing entitlement is active
 *  7.  hasMarketingPack is false when no such entitlement exists
 *  8.  hasPremiumThemePack is true when theme_pack_* entitlement is active
 *  9.  hasPremiumThemePack is false when only block-pack entitlements exist
 * 10.  events outside the window are excluded from all counts
 * 11.  stores from another agency are never listed in storeActivity
 * 12.  trend passes through from AgencyHealthService
 * 13.  aliveStores() helper returns only alive entries
 * 14.  calmStores() helper returns only calm entries
 * 15.  canAccess() returns false when no authenticated member
 * 16.  canAccess() returns true for owner role
 * 17.  canAccess() returns true for admin role
 * 18.  canAccess() returns false for plain member role
 * 19.  insightsData() returns correctly populated DTO via page
 */
class AgencyInsightsTest extends CentralTestCase
{
    private static int $seq = 0;

    // ── Helpers ───────────────────────────────────────────────────────────────

    private function makeAgency(): Agency
    {
        self::$seq++;

        return Agency::create([
            'name' => 'Insights Agency '.self::$seq,
            'slug' => 'insights-agency-'.self::$seq,
            'brand_name' => 'Insights Agency '.self::$seq,
            'status' => 'active',
            'billing_type' => 'monthly',
        ]);
    }

    private function makeTenant(Agency $agency): string
    {
        self::$seq++;
        $id = 'insights-store-'.self::$seq;

        DB::connection('central')->table('tenants')->insert([
            'id' => $id,
            'name' => 'Insights Store '.self::$seq,
            'status' => 'active',
            'agency_id' => $agency->id,
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        return $id;
    }

    private function track(
        Agency $agency,
        string $eventType,
        int $count = 1,
        ?string $tenantId = null,
        ?\DateTime $at = null,
    ): void {
        for ($i = 0; $i < $count; $i++) {
            UsageEvent::create([
                'agency_id' => $agency->id,
                'tenant_id' => $tenantId,
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

    private function grantEntitlement(Agency $agency, string $code, string $type = PluginCatalogItem::TYPE_BLOCK_PACK): AgencyEntitlement
    {
        $item = PluginCatalogItem::firstOrCreate(
            ['code' => $code],
            [
                'type' => $type,
                'name' => ucwords(str_replace('_', ' ', $code)),
                'status' => PluginCatalogItem::STATUS_ACTIVE,
            ],
        );

        return AgencyEntitlement::create([
            'agency_id' => $agency->id,
            'catalog_item_id' => $item->id,
            'source' => AgencyEntitlement::SOURCE_MANUAL,
            'status' => AgencyEntitlement::STATUS_ACTIVE,
        ]);
    }

    private function makeUser(): User
    {
        self::$seq++;

        return User::on('central')->create([
            'name' => 'User '.self::$seq,
            'email' => 'user'.self::$seq.'@example.com',
            'password' => bcrypt('password'),
        ]);
    }

    private function makeMember(Agency $agency, User $user, string $role = AgencyMember::ROLE_OWNER): AgencyMember
    {
        return AgencyMember::create([
            'agency_id' => $agency->id,
            'user_id' => $user->id,
            'role' => $role,
            'status' => AgencyMember::STATUS_ACTIVE,
        ]);
    }

    private function pageFor(Agency $agency): AgencyInsightsPage
    {
        app()->instance('current_agency', $agency);

        return new AgencyInsightsPage;
    }

    private function svc(): AgencyInsightsService
    {
        return app(AgencyInsightsService::class);
    }

    // ── 1. Active stores count ────────────────────────────────────────────────

    public function test_active_stores_count_reflects_tenants_with_storefront_renders(): void
    {
        $agency = $this->makeAgency();
        $t1 = $this->makeTenant($agency);
        $t2 = $this->makeTenant($agency);
        $this->makeTenant($agency); // no renders

        $this->trackStorefront($agency, $t1, 3);
        $this->trackStorefront($agency, $t2, 1);

        $dto = $this->svc()->forAgency($agency);

        $this->assertSame(2, $dto->activeStoresCount);
    }

    // ── 2. Total stores count ─────────────────────────────────────────────────

    public function test_total_stores_count_includes_all_tenants(): void
    {
        $agency = $this->makeAgency();
        $this->makeTenant($agency);
        $this->makeTenant($agency);
        $this->makeTenant($agency);

        $dto = $this->svc()->forAgency($agency);

        $this->assertSame(3, $dto->totalStoresCount);
    }

    // ── 3. Calm stores ────────────────────────────────────────────────────────

    public function test_stores_without_renders_have_alive_false(): void
    {
        $agency = $this->makeAgency();
        $activeId = $this->makeTenant($agency);
        $calmId = $this->makeTenant($agency);

        $this->trackStorefront($agency, $activeId, 2);

        $dto = $this->svc()->forAgency($agency);

        $aliveIds = array_column($dto->aliveStores(), 'id');
        $calmIds = array_column($dto->calmStores(), 'id');

        $this->assertContains($activeId, $aliveIds);
        $this->assertContains($calmId, $calmIds);
        $this->assertNotContains($calmId, $aliveIds);
    }

    // ── 4. Layout updates ─────────────────────────────────────────────────────

    public function test_layout_updates_reflects_layout_saved_count(): void
    {
        $agency = $this->makeAgency();
        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 7);

        $dto = $this->svc()->forAgency($agency);

        $this->assertSame(7, $dto->layoutUpdates);
    }

    // ── 5. Marketing blocks used ──────────────────────────────────────────────

    public function test_marketing_blocks_used_reflects_premium_block_rendered(): void
    {
        $agency = $this->makeAgency();
        $this->track($agency, UsageEvent::EVENT_PREMIUM_BLOCK_RENDERED, 12);

        $dto = $this->svc()->forAgency($agency);

        $this->assertSame(12, $dto->marketingBlocksUsed);
    }

    // ── 6. hasMarketingPack = true ────────────────────────────────────────────

    public function test_has_marketing_pack_true_when_entitlement_active(): void
    {
        $agency = $this->makeAgency();
        $this->grantEntitlement($agency, 'block_pack_marketing');

        $dto = $this->svc()->forAgency($agency);

        $this->assertTrue($dto->hasMarketingPack);
        $this->assertContains('block_pack_marketing', $dto->premiumPackCodes);
    }

    // ── 7. hasMarketingPack = false ───────────────────────────────────────────

    public function test_has_marketing_pack_false_when_no_entitlement(): void
    {
        $agency = $this->makeAgency();

        $dto = $this->svc()->forAgency($agency);

        $this->assertFalse($dto->hasMarketingPack);
    }

    // ── 8. hasPremiumThemePack = true ─────────────────────────────────────────

    public function test_has_premium_theme_pack_true_for_theme_pack_entitlement(): void
    {
        $agency = $this->makeAgency();
        $this->grantEntitlement($agency, 'theme_pack_editorial', PluginCatalogItem::TYPE_THEME_PACK);

        $dto = $this->svc()->forAgency($agency);

        $this->assertTrue($dto->hasPremiumThemePack);
    }

    // ── 9. hasPremiumThemePack = false ────────────────────────────────────────

    public function test_has_premium_theme_pack_false_when_only_block_entitlements(): void
    {
        $agency = $this->makeAgency();
        $this->grantEntitlement($agency, 'block_pack_marketing');

        $dto = $this->svc()->forAgency($agency);

        $this->assertFalse($dto->hasPremiumThemePack);
    }

    // ── 10. Events outside window excluded ───────────────────────────────────

    public function test_events_outside_window_are_excluded(): void
    {
        $agency = $this->makeAgency();
        $oldDate = now()->subDays(45);

        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 10, at: $oldDate);
        $this->track($agency, UsageEvent::EVENT_PREMIUM_BLOCK_RENDERED, 5, at: $oldDate);

        $tenantId = $this->makeTenant($agency);
        UsageEvent::create([
            'agency_id' => $agency->id,
            'tenant_id' => $tenantId,
            'event_type' => UsageEvent::EVENT_STOREFRONT_RENDERED,
            'event_group' => UsageEvent::GROUP_STOREFRONT,
            'occurred_at' => $oldDate,
        ]);

        $dto = $this->svc()->forAgency($agency, 30);

        $this->assertSame(0, $dto->layoutUpdates);
        $this->assertSame(0, $dto->marketingBlocksUsed);
        $this->assertSame(0, $dto->activeStoresCount);
    }

    // ── 11. Cross-agency isolation ────────────────────────────────────────────

    public function test_stores_from_another_agency_are_not_listed(): void
    {
        $agencyA = $this->makeAgency();
        $agencyB = $this->makeAgency();

        $ownStore = $this->makeTenant($agencyA);
        $otherStore = $this->makeTenant($agencyB);

        $this->trackStorefront($agencyA, $ownStore);
        $this->trackStorefront($agencyB, $otherStore);

        $dto = $this->svc()->forAgency($agencyA);

        $ids = array_column($dto->storeActivity, 'id');

        $this->assertContains($ownStore, $ids);
        $this->assertNotContains($otherStore, $ids);
    }

    // ── 12. Trend passes through ──────────────────────────────────────────────

    public function test_trend_passes_through_from_health_service(): void
    {
        $agency = $this->makeAgency();

        // previous window: 5 events 60 days ago
        $prevDate = now()->subDays(45);
        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 5, at: $prevDate);

        // current window: 10 events now (100% growth → Growing)
        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 10);

        $dto = $this->svc()->forAgency($agency, 30);

        $this->assertSame(TrendDirection::Growing, $dto->trend);
    }

    // ── 13. aliveStores() helper ──────────────────────────────────────────────

    public function test_alive_stores_helper_returns_only_alive_entries(): void
    {
        $agency = $this->makeAgency();
        $aliveId = $this->makeTenant($agency);
        $this->makeTenant($agency); // calm

        $this->trackStorefront($agency, $aliveId);

        $dto = $this->svc()->forAgency($agency);

        $alive = $dto->aliveStores();

        $this->assertCount(1, $alive);
        $this->assertSame($aliveId, array_values($alive)[0]['id']);
    }

    // ── 14. calmStores() helper ───────────────────────────────────────────────

    public function test_calm_stores_helper_returns_only_calm_entries(): void
    {
        $agency = $this->makeAgency();
        $aliveId = $this->makeTenant($agency);
        $calmId = $this->makeTenant($agency);

        $this->trackStorefront($agency, $aliveId);

        $dto = $this->svc()->forAgency($agency);

        $calm = $dto->calmStores();

        $this->assertCount(1, $calm);
        $this->assertSame($calmId, array_values($calm)[0]['id']);
    }

    // ── 15. canAccess() — no member ───────────────────────────────────────────

    public function test_can_access_returns_false_when_no_member(): void
    {
        $agency = $this->makeAgency();
        app()->instance('current_agency', $agency);

        $this->assertFalse(AgencyInsightsPage::canAccess());
    }

    // ── 16. canAccess() — owner ───────────────────────────────────────────────

    public function test_can_access_returns_true_for_owner(): void
    {
        $agency = $this->makeAgency();
        $user = $this->makeUser();
        $this->makeMember($agency, $user, AgencyMember::ROLE_OWNER);

        app()->instance('current_agency', $agency);
        $this->actingAs($user);

        $this->assertTrue(AgencyInsightsPage::canAccess());
    }

    // ── 17. canAccess() — admin ───────────────────────────────────────────────

    public function test_can_access_returns_true_for_admin(): void
    {
        $agency = $this->makeAgency();
        $user = $this->makeUser();
        $this->makeMember($agency, $user, AgencyMember::ROLE_ADMIN);

        app()->instance('current_agency', $agency);
        $this->actingAs($user);

        $this->assertTrue(AgencyInsightsPage::canAccess());
    }

    // ── 18. canAccess() — plain member ───────────────────────────────────────

    public function test_can_access_returns_false_for_plain_member(): void
    {
        $agency = $this->makeAgency();
        $user = $this->makeUser();
        $this->makeMember($agency, $user, AgencyMember::ROLE_MEMBER);

        app()->instance('current_agency', $agency);
        $this->actingAs($user);

        $this->assertFalse(AgencyInsightsPage::canAccess());
    }

    // ── 19. insightsData() via page ───────────────────────────────────────────

    public function test_insights_data_returns_correctly_populated_dto(): void
    {
        $agency = $this->makeAgency();
        $tenantId = $this->makeTenant($agency);

        $this->trackStorefront($agency, $tenantId, 3);
        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 4);
        $this->grantEntitlement($agency, 'block_pack_marketing');

        $page = $this->pageFor($agency);
        $dto = $page->insightsData();

        $this->assertSame($agency->id, $dto->agencyId);
        $this->assertSame(30, $dto->windowDays);
        $this->assertSame(1, $dto->activeStoresCount);
        $this->assertSame(1, $dto->totalStoresCount);
        $this->assertSame(4, $dto->layoutUpdates);
        $this->assertTrue($dto->hasMarketingPack);
        $this->assertCount(1, $dto->storeActivity);
        $this->assertTrue($dto->storeActivity[0]['alive']);
    }
}
