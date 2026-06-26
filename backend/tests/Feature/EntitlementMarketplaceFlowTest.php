<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\Agency;
use App\Models\Central\AgencyEntitlement;
use App\Models\Central\Plan;
use App\Models\Central\PluginCatalogItem;
use App\Services\FeatureAccessService;
use Tests\CentralTestCase;

/**
 * Covers the entitlement / marketplace feature-access lifecycle.
 *
 * Tests:
 *  1. Agency acquires plugin → AgencyEntitlement created and active
 *  2. Agency without entitlement cannot use the feature (canUseFeature=false)
 *  3. Agency acquires theme pack → ThemePack entitlement active
 *  4. Expired entitlement → access denied (isActive=false)
 *  5. Manually revoked entitlement → access denied immediately
 *  6. TODO — fork premium theme without entitlement → 403 (ThemeForkResolver HTTP)
 *  7. Free-plan agency blocked from premium feature → canUseFeature returns false
 */
class EntitlementMarketplaceFlowTest extends CentralTestCase
{
    // ── Helpers ───────────────────────────────────────────────────────────────

    private static int $seq = 0;

    private function makePlan(array $limits = []): Plan
    {
        self::$seq++;

        return Plan::create([
            'name' => 'Plan '.self::$seq,
            'slug' => 'plan-'.self::$seq,
            'price' => 29,
            'billing_interval' => 'month',
            'is_active' => true,
            'sort_order' => self::$seq,
            'limits' => $limits,
        ]);
    }

    private function makeAgency(?Plan $plan = null): Agency
    {
        self::$seq++;

        $agency = Agency::create([
            'name' => 'Agency '.self::$seq,
            'slug' => 'agency-'.self::$seq,
            'brand_name' => 'Agency '.self::$seq,
            'status' => 'active',
            'billing_type' => 'monthly',
        ]);

        if ($plan) {
            $agency->update(['plan_id' => $plan->id]);
            $agency->load('plan');
        }

        return $agency;
    }

    private function makeCatalogItem(string $code, string $type = PluginCatalogItem::TYPE_PLUGIN): PluginCatalogItem
    {
        return PluginCatalogItem::create([
            'code' => $code,
            'type' => $type,
            'name' => $code,
            'status' => PluginCatalogItem::STATUS_ACTIVE,
        ]);
    }

    /** Create an active entitlement that starts now and never expires. */
    private function grantEntitlement(Agency $agency, PluginCatalogItem $item, string $source = AgencyEntitlement::SOURCE_LICENSE): AgencyEntitlement
    {
        return AgencyEntitlement::create([
            'agency_id' => $agency->id,
            'catalog_item_id' => $item->id,
            'source' => $source,
            'status' => AgencyEntitlement::STATUS_ACTIVE,
            'starts_at' => now()->subSecond(),
        ]);
    }

    private function service(): FeatureAccessService
    {
        return app(FeatureAccessService::class);
    }

    // ── Test 1 ────────────────────────────────────────────────────────────────

    public function test_granting_plugin_entitlement_makes_it_active(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem('seo_plugin', PluginCatalogItem::TYPE_PLUGIN);

        // ── Grant entitlement (simulates marketplace purchase) ────────────────
        $entitlement = $this->grantEntitlement($agency, $item);

        $this->assertTrue($entitlement->isActive());
        $this->assertEquals(AgencyEntitlement::STATUS_ACTIVE, $entitlement->status);
        $this->assertEquals($agency->id, $entitlement->agency_id);
        $this->assertEquals($item->id, $entitlement->catalog_item_id);
    }

    public function test_agency_with_active_entitlement_can_use_feature(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem('advanced_analytics');

        $this->grantEntitlement($agency, $item);

        $canUse = $this->service()->canUseFeature($agency, 'advanced_analytics');

        $this->assertTrue($canUse);
    }

    // ── Test 2 ────────────────────────────────────────────────────────────────

    public function test_agency_without_entitlement_cannot_use_feature(): void
    {
        $agency = $this->makeAgency(); // no plan, no entitlement

        $canUse = $this->service()->canUseFeature($agency, 'advanced_analytics');

        $this->assertFalse($canUse);
    }

    public function test_feature_access_service_has_active_entitlement_returns_false_without_it(): void
    {
        $agency = $this->makeAgency();

        $hasEntitlement = $this->service()->hasActiveEntitlement($agency, 'nonexistent_feature');

        $this->assertFalse($hasEntitlement);
    }

    // ── Test 3 ────────────────────────────────────────────────────────────────

    public function test_granting_theme_pack_entitlement_enables_theme_feature(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem('theme_pack_editorial', PluginCatalogItem::TYPE_THEME_PACK);

        $this->grantEntitlement($agency, $item, AgencyEntitlement::SOURCE_MANUAL);

        $canUse = $this->service()->canUseFeature($agency, 'theme_pack_editorial');

        $this->assertTrue($canUse);
    }

    // ── Test 4 ────────────────────────────────────────────────────────────────

    public function test_expired_entitlement_is_not_active(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem('block_pack_v1', PluginCatalogItem::TYPE_BLOCK_PACK);

        // ── Entitlement with past ends_at ─────────────────────────────────────
        $entitlement = AgencyEntitlement::create([
            'agency_id' => $agency->id,
            'catalog_item_id' => $item->id,
            'source' => AgencyEntitlement::SOURCE_LICENSE,
            'status' => AgencyEntitlement::STATUS_ACTIVE,
            'starts_at' => now()->subMonth(),
            'ends_at' => now()->subDay(), // already expired
        ]);

        $this->assertFalse($entitlement->isActive());
    }

    public function test_expired_entitlement_blocks_feature_access(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem('expire_test_feature');

        AgencyEntitlement::create([
            'agency_id' => $agency->id,
            'catalog_item_id' => $item->id,
            'source' => AgencyEntitlement::SOURCE_LICENSE,
            'status' => AgencyEntitlement::STATUS_ACTIVE,
            'starts_at' => now()->subMonth(),
            'ends_at' => now()->subDay(),
        ]);

        $canUse = $this->service()->canUseFeature($agency, 'expire_test_feature');

        $this->assertFalse($canUse);
    }

    public function test_expire_method_sets_status_to_expired(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem('expirable_plugin');
        $entitlement = $this->grantEntitlement($agency, $item);

        $entitlement->expire();
        $entitlement->refresh();

        $this->assertEquals(AgencyEntitlement::STATUS_EXPIRED, $entitlement->status);
        $this->assertFalse($entitlement->isActive());
    }

    // ── Test 5 ────────────────────────────────────────────────────────────────

    public function test_revoke_method_sets_status_to_revoked(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem('revocable_plugin');
        $entitlement = $this->grantEntitlement($agency, $item);

        $entitlement->revoke();
        $entitlement->refresh();

        $this->assertEquals(AgencyEntitlement::STATUS_REVOKED, $entitlement->status);
        $this->assertFalse($entitlement->isActive());
    }

    public function test_revoked_entitlement_blocks_feature_access_immediately(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem('revoke_test_feature');
        $entitlement = $this->grantEntitlement($agency, $item);

        // Confirm access before revocation
        $this->assertTrue($this->service()->canUseFeature($agency, 'revoke_test_feature'));

        // ── Revoke ────────────────────────────────────────────────────────────
        $entitlement->revoke();

        // FeatureAccessService caches per request — get a fresh instance
        $freshService = new FeatureAccessService;
        $canUse = $freshService->canUseFeature($agency, 'revoke_test_feature');

        $this->assertFalse($canUse);
    }

    // ── Test 6 ────────────────────────────────────────────────────────────────

    // TODO — ThemeForkResolver HTTP path requires a Filament action or API endpoint.
    // When the fork-without-entitlement gate is exposed as an HTTP route, implement:
    //
    // public function test_fork_premium_theme_without_entitlement_returns_403(): void
    // {
    //     $agency = $this->makeAgency(); // no entitlement for theme_pack_editorial
    //     $owner  = $this->makeOwner($agency);
    //     $preset = ThemePreset::create([...]);  // system theme that requires entitlement
    //     app()->instance('current_agency', $agency);
    //
    //     // TODO — verify route name for fork action
    //     $response = $this->actingAs($owner)
    //          ->post(route('filament.agency.theme-presets.fork', $preset), []);
    //     $response->assertForbidden();
    // }

    public function test_can_use_feature_returns_false_for_fork_without_entitlement(): void
    {
        // ThemeForkResolver uses FeatureAccessService internally
        $agency = $this->makeAgency(); // no plan, no entitlement

        $canFork = $this->service()->canUseFeature($agency, 'theme_pack_editorial');

        $this->assertFalse($canFork);
    }

    // ── Test 7 ────────────────────────────────────────────────────────────────

    public function test_free_plan_agency_cannot_use_premium_feature(): void
    {
        // ── Plan without premium feature in limits ────────────────────────────
        $freePlan = $this->makePlan(['white_label' => false, 'theme_pack_editorial' => false]);
        $agency = $this->makeAgency($freePlan);

        $canUse = $this->service()->canUseFeature($agency, 'theme_pack_editorial');

        $this->assertFalse($canUse);
    }

    public function test_paid_plan_with_feature_flag_grants_access(): void
    {
        $paidPlan = $this->makePlan(['theme_pack_editorial' => true]);
        $agency = $this->makeAgency($paidPlan);

        $canUse = $this->service()->canUseFeature($agency, 'theme_pack_editorial');

        $this->assertTrue($canUse);
    }

    // ── Legacy SKU expansion ──────────────────────────────────────────────────

    public function test_legacy_theme_premium_entitlement_grants_editorial_pack_access(): void
    {
        // Fase 4C: theme_premium legacy code expands to theme_pack_editorial + theme_pack_business
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem('theme_premium', PluginCatalogItem::TYPE_THEME_PACK);

        $this->grantEntitlement($agency, $item);

        $freshService = new FeatureAccessService;

        $this->assertTrue(
            $freshService->canUseFeature($agency, 'theme_pack_editorial'),
            'Legacy theme_premium should expand to theme_pack_editorial',
        );
        $this->assertTrue(
            $freshService->canUseFeature($agency, 'theme_pack_business'),
            'Legacy theme_premium should expand to theme_pack_business',
        );
    }

    // ── explainDenied ─────────────────────────────────────────────────────────

    public function test_explain_denied_returns_null_when_access_granted(): void
    {
        $plan = $this->makePlan(['some_feature' => true]);
        $agency = $this->makeAgency($plan);

        $reason = $this->service()->explainDenied($agency, 'some_feature');

        $this->assertNull($reason);
    }

    public function test_explain_denied_returns_revoked_reason_when_entitlement_revoked(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem('revoked_feature');
        $entitlement = $this->grantEntitlement($agency, $item);
        $entitlement->revoke();

        $freshService = new FeatureAccessService;
        $reason = $freshService->explainDenied($agency, 'revoked_feature');

        $this->assertStringContainsString('revocato', $reason ?? '');
    }
}
