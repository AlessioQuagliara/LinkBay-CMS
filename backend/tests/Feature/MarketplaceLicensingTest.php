<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\Agency;
use App\Models\Central\AgencyEntitlement;
use App\Models\Central\AuditEvent;
use App\Models\Central\Plan;
use App\Models\Central\PluginCatalogItem;
use App\Plugins\PluginRegistry;
use App\Plugins\ThemeDefinition;
use App\Services\FeatureAccessService;
use Tests\CentralTestCase;

/**
 * Marketplace / Licensing Foundation v1 test suite.
 *
 * Tests:
 *  1.  PluginCatalogItem can be created and persisted
 *  2.  PluginCatalogItem scopeActive filters by status
 *  3.  AgencyEntitlement grant creates active entitlement
 *  4.  AgencyEntitlement revoke sets status to revoked
 *  5.  AgencyEntitlement expire sets status to expired
 *  6.  AgencyEntitlement::isActive() with date windows
 *  7.  FeatureAccessService: access via plan
 *  8.  FeatureAccessService: access via active entitlement
 *  9.  FeatureAccessService: denied when no plan and no entitlement
 * 10.  FeatureAccessService: denied when entitlement is revoked
 * 11.  FeatureAccessService: denied when entitlement is expired
 * 12.  FeatureAccessService: denied when entitlement hasn't started yet
 * 13.  FeatureAccessService::grantedFeatures returns plan + entitlement codes
 * 14.  FeatureAccessService::explainDenied returns null when access is granted
 * 15.  FeatureAccessService::explainDenied returns reason for each denial type
 * 16.  Cross-agency isolation: agency A entitlement doesn't bleed to agency B
 * 17.  AuditEvent constants exist for entitlement events
 * 18.  Midnight premium theme is registered with featureCode = theme_premium
 * 19.  PluginRegistry has 4 themes (3 free + 1 premium)
 */
class MarketplaceLicensingTest extends CentralTestCase
{
    private static int $seq = 0;

    // ── Helpers ───────────────────────────────────────────────────────────────

    private function service(): FeatureAccessService
    {
        return app(FeatureAccessService::class);
    }

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

    private function makePlanWithFeature(string $featureCode): Plan
    {
        self::$seq++;

        return Plan::create([
            'name' => 'Plan '.self::$seq,
            'slug' => 'plan-'.self::$seq,
            'price' => 99,
            'billing_interval' => 'month',
            'features' => [],
            'limits' => [$featureCode => true],
            'is_active' => true,
        ]);
    }

    private function makeCatalogItem(string $code = 'theme_premium', string $status = PluginCatalogItem::STATUS_ACTIVE): PluginCatalogItem
    {
        return PluginCatalogItem::create([
            'code' => $code,
            'type' => PluginCatalogItem::TYPE_FEATURE,
            'name' => ucfirst(str_replace('_', ' ', $code)),
            'status' => $status,
        ]);
    }

    private function grantEntitlement(Agency $agency, PluginCatalogItem $item, array $overrides = []): AgencyEntitlement
    {
        return AgencyEntitlement::create(array_merge([
            'agency_id' => $agency->id,
            'catalog_item_id' => $item->id,
            'source' => AgencyEntitlement::SOURCE_MANUAL,
            'status' => AgencyEntitlement::STATUS_ACTIVE,
        ], $overrides));
    }

    // ── 1. PluginCatalogItem persistence ─────────────────────────────────────

    public function test_plugin_catalog_item_can_be_created(): void
    {
        $item = $this->makeCatalogItem('block_pack_pro');

        $this->assertDatabaseHas('plugin_catalog_items', [
            'code' => 'block_pack_pro',
            'type' => PluginCatalogItem::TYPE_FEATURE,
            'status' => PluginCatalogItem::STATUS_ACTIVE,
        ], 'central');

        $this->assertTrue($item->isActive());
    }

    // ── 2. scopeActive ────────────────────────────────────────────────────────

    public function test_scope_active_filters_by_status(): void
    {
        $this->makeCatalogItem('feature_a', PluginCatalogItem::STATUS_ACTIVE);
        $this->makeCatalogItem('feature_b', PluginCatalogItem::STATUS_DRAFT);
        $this->makeCatalogItem('feature_c', PluginCatalogItem::STATUS_ARCHIVED);

        $active = PluginCatalogItem::active()->pluck('code');

        $this->assertContains('feature_a', $active);
        $this->assertNotContains('feature_b', $active);
        $this->assertNotContains('feature_c', $active);
    }

    // ── 3. Grant entitlement ──────────────────────────────────────────────────

    public function test_granting_entitlement_creates_active_record(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem();

        $entitlement = $this->grantEntitlement($agency, $item);

        $this->assertDatabaseHas('agency_entitlements', [
            'agency_id' => $agency->id,
            'catalog_item_id' => $item->id,
            'status' => AgencyEntitlement::STATUS_ACTIVE,
        ], 'central');

        $this->assertTrue($entitlement->isActive());
    }

    // ── 4. Revoke entitlement ─────────────────────────────────────────────────

    public function test_revoke_sets_status_to_revoked(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem();
        $entitlement = $this->grantEntitlement($agency, $item);

        $entitlement->revoke();

        $this->assertDatabaseHas('agency_entitlements', [
            'id' => $entitlement->id,
            'status' => AgencyEntitlement::STATUS_REVOKED,
        ], 'central');

        $this->assertFalse($entitlement->fresh()->isActive());
    }

    // ── 5. Expire entitlement ─────────────────────────────────────────────────

    public function test_expire_sets_status_to_expired(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem();
        $entitlement = $this->grantEntitlement($agency, $item);

        $entitlement->expire();

        $this->assertEquals(AgencyEntitlement::STATUS_EXPIRED, $entitlement->fresh()->status);
        $this->assertFalse($entitlement->fresh()->isActive());
    }

    // ── 6. isActive with date windows ─────────────────────────────────────────

    public function test_is_active_respects_date_windows(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem();

        $futureStart = $this->grantEntitlement($agency, $item, ['starts_at' => now()->addDay()]);
        $this->assertFalse($futureStart->isActive(), 'Should not be active when starts_at is in the future');

        // Unique constraint: update the existing entitlement instead of creating another
        $futureStart->update(['starts_at' => now()->subDay(), 'ends_at' => now()->subHour()]);
        $this->assertFalse($futureStart->fresh()->isActive(), 'Should not be active when ends_at is in the past');

        $futureStart->update(['starts_at' => now()->subDay(), 'ends_at' => now()->addDay()]);
        $this->assertTrue($futureStart->fresh()->isActive(), 'Should be active when within valid date window');
    }

    // ── 7. Access via plan ────────────────────────────────────────────────────

    public function test_can_use_feature_returns_true_via_plan(): void
    {
        $plan = $this->makePlanWithFeature('theme_premium');
        $agency = $this->makeAgency($plan);

        $this->assertTrue($this->service()->canUseFeature($agency, 'theme_premium'));
    }

    // ── 8. Access via active entitlement ──────────────────────────────────────

    public function test_can_use_feature_returns_true_via_active_entitlement(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem();
        $this->grantEntitlement($agency, $item);

        $this->assertTrue($this->service()->canUseFeature($agency, 'theme_premium'));
        $this->assertTrue($this->service()->hasActiveEntitlement($agency, 'theme_premium'));
    }

    // ── 9. Denied with no access ──────────────────────────────────────────────

    public function test_can_use_feature_returns_false_when_no_plan_and_no_entitlement(): void
    {
        $agency = $this->makeAgency();

        $this->assertFalse($this->service()->canUseFeature($agency, 'theme_premium'));
        $this->assertFalse($this->service()->hasActiveEntitlement($agency, 'theme_premium'));
    }

    // ── 10. Denied when revoked ───────────────────────────────────────────────

    public function test_can_use_feature_returns_false_when_entitlement_is_revoked(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem();
        $entitlement = $this->grantEntitlement($agency, $item);
        $entitlement->revoke();

        $this->assertFalse($this->service()->canUseFeature($agency, 'theme_premium'));
    }

    // ── 11. Denied when expired ───────────────────────────────────────────────

    public function test_can_use_feature_returns_false_when_entitlement_is_expired(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem();
        $entitlement = $this->grantEntitlement($agency, $item, [
            'ends_at' => now()->subHour(),
        ]);

        $this->assertFalse($this->service()->canUseFeature($agency, 'theme_premium'));
        $this->assertFalse($entitlement->isActive());
    }

    // ── 12. Denied when not yet started ──────────────────────────────────────

    public function test_can_use_feature_returns_false_when_entitlement_not_yet_started(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem();
        $this->grantEntitlement($agency, $item, ['starts_at' => now()->addDay()]);

        $this->assertFalse($this->service()->canUseFeature($agency, 'theme_premium'));
    }

    // ── 13. grantedFeatures returns union of plan + entitlements ─────────────

    public function test_granted_features_returns_plan_and_entitlement_codes(): void
    {
        $plan = $this->makePlanWithFeature('advanced_analytics');
        $agency = $this->makeAgency($plan);

        $premiumItem = $this->makeCatalogItem('theme_premium');
        $this->grantEntitlement($agency, $premiumItem);

        $granted = $this->service()->grantedFeatures($agency);

        $this->assertContains('advanced_analytics', $granted);
        $this->assertContains('theme_premium', $granted);
    }

    // ── 14. explainDenied returns null when access is granted ─────────────────

    public function test_explain_denied_returns_null_when_access_is_granted(): void
    {
        $plan = $this->makePlanWithFeature('theme_premium');
        $agency = $this->makeAgency($plan);

        $this->assertNull($this->service()->explainDenied($agency, 'theme_premium'));
    }

    // ── 15. explainDenied returns reason for each denial type ─────────────────

    public function test_explain_denied_returns_correct_reasons(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem();

        // No entitlement at all
        $noAccess = $this->service()->explainDenied($agency, 'theme_premium');
        $this->assertNotNull($noAccess);
        $this->assertStringContainsString('nessun entitlement', $noAccess);

        // Revoked
        $entitlement = $this->grantEntitlement($agency, $item);
        $entitlement->revoke();
        $revoked = $this->service()->explainDenied($agency, 'theme_premium');
        $this->assertStringContainsString('revocato', $revoked, 'Should mention revocation');

        // Expired
        $entitlement->update(['status' => AgencyEntitlement::STATUS_EXPIRED]);
        $expired = $this->service()->explainDenied($agency, 'theme_premium');
        $this->assertStringContainsString('scaduto', $expired, 'Should mention expiry');
    }

    // ── 16. Cross-agency isolation ────────────────────────────────────────────

    public function test_entitlement_for_agency_a_does_not_grant_access_to_agency_b(): void
    {
        $agencyA = $this->makeAgency();
        $agencyB = $this->makeAgency();
        $item = $this->makeCatalogItem();

        $this->grantEntitlement($agencyA, $item);

        $this->assertTrue($this->service()->canUseFeature($agencyA, 'theme_premium'));
        $this->assertFalse($this->service()->canUseFeature($agencyB, 'theme_premium'));
    }

    // ── 17. AuditEvent constants ──────────────────────────────────────────────

    public function test_audit_event_constants_exist_for_entitlement_events(): void
    {
        $this->assertEquals('entitlement.granted', AuditEvent::EVENT_ENTITLEMENT_GRANTED);
        $this->assertEquals('entitlement.revoked', AuditEvent::EVENT_ENTITLEMENT_REVOKED);
        $this->assertArrayHasKey('entitlement.granted', AuditEvent::EVENT_LABELS);
        $this->assertArrayHasKey('entitlement.revoked', AuditEvent::EVENT_LABELS);
    }

    // ── 18. Midnight theme has featureCode = theme_pack_editorial ────────────────────

    public function test_midnight_theme_is_registered_with_feature_code(): void
    {
        $registry = app(PluginRegistry::class);

        $this->assertTrue($registry->hasTheme('midnight'), 'Midnight theme must be in the registry');

        $definition = $registry->getTheme('midnight');
        $this->assertInstanceOf(ThemeDefinition::class, $definition);
        $this->assertEquals('theme_pack_editorial', $definition->featureCode);
    }

    // ── 19. Registry has all expected themes ──────────────────────────────────

    public function test_registry_has_all_themes_including_premium_pack(): void
    {
        $registry = app(PluginRegistry::class);

        // 4 core (ocean, slate, sand, midnight) + 3 premium pack (noir, atelier, meridian)
        $this->assertCount(7, $registry->themes(), 'Registry must have all 7 registered themes');

        $this->assertNull($registry->getTheme('ocean')->featureCode, 'Ocean must be free');
        $this->assertNull($registry->getTheme('slate')->featureCode, 'Slate must be free');
        $this->assertNull($registry->getTheme('sand')->featureCode, 'Sand must be free');
        $this->assertNotNull($registry->getTheme('midnight')->featureCode, 'Midnight must be gated');
        $this->assertNotNull($registry->getTheme('noir')->featureCode, 'Noir must be gated');
        $this->assertNotNull($registry->getTheme('atelier')->featureCode, 'Atelier must be gated');
        $this->assertNotNull($registry->getTheme('meridian')->featureCode, 'Meridian must be gated');
    }
}
