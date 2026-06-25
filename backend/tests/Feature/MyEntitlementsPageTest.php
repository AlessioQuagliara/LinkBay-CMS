<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Filament\Agency\Pages\MyEntitlementsPage;
use App\Models\Central\Agency;
use App\Models\Central\AgencyEntitlement;
use App\Models\Central\AgencyMember;
use App\Models\Central\Plan;
use App\Models\Central\PluginCatalogItem;
use App\Models\User;
use Tests\CentralTestCase;

/**
 * MyEntitlementsPage test suite.
 *
 * Tests:
 *  1.  canAccess() returns false when no authenticated member
 *  2.  canAccess() returns true for owner role
 *  3.  canAccess() returns true for admin role
 *  4.  canAccess() returns false for plain member role
 *  5.  planFeatures() returns empty array when agency has no plan
 *  6.  planFeatures() returns truthy limit keys from current plan
 *  7.  activeEntitlements() returns empty collection when no entitlements
 *  8.  activeEntitlements() returns only active entitlements for current agency
 *  9.  activeEntitlements() agency scoping — does not leak data from other agencies
 * 10.  inactiveEntitlements() returns expired and revoked entitlements
 * 11.  inactiveEntitlements() does not return active entitlements
 * 12.  summaryStats() returns zeros when no plan and no entitlements
 * 13.  summaryStats() counts plan features + active entitlements correctly
 * 14.  summaryStats() counts inactive (expired/revoked) correctly
 */
class MyEntitlementsPageTest extends CentralTestCase
{
    private static int $seq = 0;

    // ── Helpers ───────────────────────────────────────────────────────────────

    private function makeAgency(?Plan $plan = null): Agency
    {
        self::$seq++;

        return Agency::create([
            'name' => 'Agency '.self::$seq,
            'slug' => 'agency-'.self::$seq,
            'brand_name' => 'Agency '.self::$seq,
            'status' => 'active',
            'billing_type' => 'monthly',
            'plan_id' => $plan?->id,
        ]);
    }

    private function makePlan(array $limits = []): Plan
    {
        self::$seq++;

        return Plan::create([
            'name' => 'Plan '.self::$seq,
            'slug' => 'plan-'.self::$seq,
            'price' => 49,
            'billing_interval' => 'month',
            'features' => [],
            'limits' => $limits,
            'is_active' => true,
        ]);
    }

    private function makeCatalogItem(string $code, string $type = PluginCatalogItem::TYPE_BLOCK_PACK): PluginCatalogItem
    {
        return PluginCatalogItem::firstOrCreate(
            ['code' => $code],
            [
                'type' => $type,
                'name' => ucwords(str_replace('_', ' ', $code)),
                'status' => PluginCatalogItem::STATUS_ACTIVE,
            ]
        );
    }

    private function grantEntitlement(Agency $agency, PluginCatalogItem $item, string $status = AgencyEntitlement::STATUS_ACTIVE): AgencyEntitlement
    {
        return AgencyEntitlement::create([
            'agency_id' => $agency->id,
            'catalog_item_id' => $item->id,
            'source' => AgencyEntitlement::SOURCE_MANUAL,
            'status' => $status,
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

    private function pageFor(Agency $agency): MyEntitlementsPage
    {
        app()->instance('current_agency', $agency);
        $agency->load('plan');

        return new MyEntitlementsPage;
    }

    // ── 1–4. canAccess() ──────────────────────────────────────────────────────

    public function test_can_access_returns_false_when_no_member(): void
    {
        $agency = $this->makeAgency();
        app()->instance('current_agency', $agency);

        $this->assertFalse(MyEntitlementsPage::canAccess());
    }

    public function test_can_access_returns_true_for_owner(): void
    {
        $agency = $this->makeAgency();
        $user = $this->makeUser();
        $this->makeMember($agency, $user, AgencyMember::ROLE_OWNER);

        app()->instance('current_agency', $agency);
        $this->actingAs($user);

        $this->assertTrue(MyEntitlementsPage::canAccess());
    }

    public function test_can_access_returns_true_for_admin(): void
    {
        $agency = $this->makeAgency();
        $user = $this->makeUser();
        $this->makeMember($agency, $user, AgencyMember::ROLE_ADMIN);

        app()->instance('current_agency', $agency);
        $this->actingAs($user);

        $this->assertTrue(MyEntitlementsPage::canAccess());
    }

    public function test_can_access_returns_false_for_plain_member(): void
    {
        $agency = $this->makeAgency();
        $user = $this->makeUser();
        $this->makeMember($agency, $user, AgencyMember::ROLE_MEMBER);

        app()->instance('current_agency', $agency);
        $this->actingAs($user);

        $this->assertFalse(MyEntitlementsPage::canAccess());
    }

    // ── 5–6. planFeatures() ───────────────────────────────────────────────────

    public function test_plan_features_empty_without_plan(): void
    {
        $agency = $this->makeAgency(); // no plan
        $page = $this->pageFor($agency);

        $this->assertEmpty($page->planFeatures());
    }

    public function test_plan_features_returns_truthy_limit_keys(): void
    {
        $plan = $this->makePlan([
            'block_pack_marketing' => true,
            'theme_premium' => true,
            'max_stores' => 10,
            'disabled_feature' => false,
        ]);
        $agency = $this->makeAgency($plan);
        $page = $this->pageFor($agency);

        $features = $page->planFeatures();

        $this->assertContains('block_pack_marketing', $features);
        $this->assertContains('theme_premium', $features);
        $this->assertContains('max_stores', $features);
        $this->assertNotContains('disabled_feature', $features);
    }

    // ── 7–9. activeEntitlements() ────────────────────────────────────────────

    public function test_active_entitlements_empty_when_none(): void
    {
        $agency = $this->makeAgency();
        $page = $this->pageFor($agency);

        $this->assertTrue($page->activeEntitlements()->isEmpty());
    }

    public function test_active_entitlements_returns_only_active_records(): void
    {
        $agency = $this->makeAgency();
        $item1 = $this->makeCatalogItem('pack_a');
        $item2 = $this->makeCatalogItem('pack_b');
        $item3 = $this->makeCatalogItem('pack_c');

        $this->grantEntitlement($agency, $item1, AgencyEntitlement::STATUS_ACTIVE);
        $this->grantEntitlement($agency, $item2, AgencyEntitlement::STATUS_EXPIRED);
        $this->grantEntitlement($agency, $item3, AgencyEntitlement::STATUS_REVOKED);

        $page = $this->pageFor($agency);
        $active = $page->activeEntitlements();

        $this->assertCount(1, $active);
        $this->assertEquals('pack_a', $active->first()->catalogItem->code);
    }

    public function test_active_entitlements_scoped_to_current_agency(): void
    {
        $agencyA = $this->makeAgency();
        $agencyB = $this->makeAgency();
        $item = $this->makeCatalogItem('shared_pack');

        $this->grantEntitlement($agencyA, $item);
        $this->grantEntitlement($agencyB, $item);

        // Page for agency A must not see agency B's entitlements
        $page = $this->pageFor($agencyA);
        $active = $page->activeEntitlements();

        $this->assertCount(1, $active);
        $this->assertEquals($agencyA->id, $active->first()->agency_id);
    }

    // ── 10–11. inactiveEntitlements() ────────────────────────────────────────

    public function test_inactive_entitlements_returns_expired_and_revoked(): void
    {
        $agency = $this->makeAgency();
        $expired = $this->makeCatalogItem('pack_expired');
        $revoked = $this->makeCatalogItem('pack_revoked');
        $active = $this->makeCatalogItem('pack_active');

        $this->grantEntitlement($agency, $expired, AgencyEntitlement::STATUS_EXPIRED);
        $this->grantEntitlement($agency, $revoked, AgencyEntitlement::STATUS_REVOKED);
        $this->grantEntitlement($agency, $active, AgencyEntitlement::STATUS_ACTIVE);

        $page = $this->pageFor($agency);
        $inactive = $page->inactiveEntitlements();

        $this->assertCount(2, $inactive);
        $codes = $inactive->pluck('catalogItem.code')->all();
        $this->assertContains('pack_expired', $codes);
        $this->assertContains('pack_revoked', $codes);
        $this->assertNotContains('pack_active', $codes);
    }

    public function test_inactive_entitlements_does_not_include_active(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem('active_only_pack');
        $this->grantEntitlement($agency, $item, AgencyEntitlement::STATUS_ACTIVE);

        $page = $this->pageFor($agency);

        $this->assertTrue($page->inactiveEntitlements()->isEmpty());
    }

    // ── 12–14. summaryStats() ────────────────────────────────────────────────

    public function test_summary_stats_all_zero_without_plan_or_entitlements(): void
    {
        $agency = $this->makeAgency();
        $page = $this->pageFor($agency);

        $stats = $page->summaryStats();

        $this->assertEquals(0, $stats['active_features']);
        $this->assertEquals(0, $stats['premium_addons']);
        $this->assertEquals(0, $stats['inactive_count']);
    }

    public function test_summary_stats_counts_plan_features_and_entitlements(): void
    {
        $plan = $this->makePlan([
            'block_pack_marketing' => true,
            'theme_premium' => true,
        ]);
        $agency = $this->makeAgency($plan);
        $item = $this->makeCatalogItem('extra_pack');
        $this->grantEntitlement($agency, $item);

        $page = $this->pageFor($agency);
        $stats = $page->summaryStats();

        // 2 plan features + 1 active entitlement = 3 active features total
        $this->assertEquals(3, $stats['active_features']);
        // 1 active entitlement (add-on)
        $this->assertEquals(1, $stats['premium_addons']);
        $this->assertEquals(0, $stats['inactive_count']);
    }

    public function test_summary_stats_counts_inactive_separately(): void
    {
        $agency = $this->makeAgency();
        $item1 = $this->makeCatalogItem('revoked_pack');
        $item2 = $this->makeCatalogItem('expired_pack');
        $item3 = $this->makeCatalogItem('live_pack');

        $this->grantEntitlement($agency, $item1, AgencyEntitlement::STATUS_REVOKED);
        $this->grantEntitlement($agency, $item2, AgencyEntitlement::STATUS_EXPIRED);
        $this->grantEntitlement($agency, $item3, AgencyEntitlement::STATUS_ACTIVE);

        $page = $this->pageFor($agency);
        $stats = $page->summaryStats();

        $this->assertEquals(1, $stats['active_features']);
        $this->assertEquals(1, $stats['premium_addons']);
        $this->assertEquals(2, $stats['inactive_count']);
    }
}
