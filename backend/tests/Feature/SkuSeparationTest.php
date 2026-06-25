<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\Agency;
use App\Models\Central\AgencyEntitlement;
use App\Models\Central\Plan;
use App\Models\Central\PluginCatalogItem;
use App\Plugins\PluginRegistry;
use App\Plugins\PremiumThemePack\PremiumThemePackServiceProvider;
use App\Services\FeatureAccessService;
use App\Services\PremiumPackConfig;
use Tests\CentralTestCase;

/**
 * SKU Separation — Fase 4C test suite.
 *
 * Verifies that theme_premium has been split into two distinct SKUs:
 *   theme_pack_editorial → Midnight, Noir
 *   theme_pack_business  → Atelier, Meridian
 *
 * Also verifies backward compatibility: legacy theme_premium entitlements/plans
 * continue to grant access to all premium themes via FeatureAccessService.
 *
 * Tests:
 *  1.  theme_pack_editorial entitlement grants access to Midnight
 *  2.  theme_pack_editorial entitlement grants access to Noir
 *  3.  theme_pack_editorial entitlement does NOT grant access to Atelier
 *  4.  theme_pack_editorial entitlement does NOT grant access to Meridian
 *  5.  theme_pack_business entitlement grants access to Atelier
 *  6.  theme_pack_business entitlement grants access to Meridian
 *  7.  theme_pack_business entitlement does NOT grant access to Midnight
 *  8.  theme_pack_business entitlement does NOT grant access to Noir
 *  9.  Legacy theme_premium entitlement grants access to all 4 premium themes
 * 10.  Legacy theme_premium plan grants access to all 4 premium themes
 * 11.  PremiumPackConfig has editorial and business packs with correct themes listed
 * 12.  unavailableFor() with editorial entitlement excludes editorial but shows business
 * 13.  unavailableFor() with legacy theme_premium entitlement excludes both theme packs
 * 14.  unavailableFor() with editorial + business entitlements excludes both theme packs
 */
class SkuSeparationTest extends CentralTestCase
{
    private static int $seq = 0;

    // ── Helpers ───────────────────────────────────────────────────────────────

    private function makeAgency(?Plan $plan = null): Agency
    {
        self::$seq++;

        return Agency::create([
            'name' => 'SKU Agency '.self::$seq,
            'slug' => 'sku-agency-'.self::$seq,
            'brand_name' => 'SKU Agency '.self::$seq,
            'status' => 'active',
            'billing_type' => 'monthly',
            'plan_id' => $plan?->id,
        ]);
    }

    private function makePlanWithFeature(string $code): Plan
    {
        self::$seq++;

        return Plan::create([
            'name' => 'SKU Plan '.self::$seq,
            'slug' => 'sku-plan-'.self::$seq,
            'price' => 99,
            'billing_interval' => 'month',
            'features' => [],
            'limits' => [$code => true],
            'is_active' => true,
        ]);
    }

    private function grantEntitlement(Agency $agency, string $code): AgencyEntitlement
    {
        $item = PluginCatalogItem::firstOrCreate(
            ['code' => $code],
            ['type' => PluginCatalogItem::TYPE_THEME_PACK, 'name' => $code, 'status' => PluginCatalogItem::STATUS_ACTIVE],
        );

        return AgencyEntitlement::create([
            'agency_id' => $agency->id,
            'catalog_item_id' => $item->id,
            'source' => AgencyEntitlement::SOURCE_MANUAL,
            'status' => AgencyEntitlement::STATUS_ACTIVE,
        ]);
    }

    private function service(): FeatureAccessService
    {
        return app(FeatureAccessService::class);
    }

    private function featureCodeFor(string $themeKey): string
    {
        return app(PluginRegistry::class)->getTheme($themeKey)->featureCode;
    }

    // ── 1-4. Editorial SKU grants Midnight + Noir only ────────────────────────

    public function test_editorial_entitlement_grants_midnight(): void
    {
        $agency = $this->makeAgency();
        $this->grantEntitlement($agency, PremiumThemePackServiceProvider::FEATURE_CODE_EDITORIAL);

        $this->assertTrue(
            $this->service()->canUseFeature($agency, $this->featureCodeFor('midnight')),
            'theme_pack_editorial entitlement must grant access to Midnight'
        );
    }

    public function test_editorial_entitlement_grants_noir(): void
    {
        $agency = $this->makeAgency();
        $this->grantEntitlement($agency, PremiumThemePackServiceProvider::FEATURE_CODE_EDITORIAL);

        $this->assertTrue(
            $this->service()->canUseFeature($agency, $this->featureCodeFor('noir')),
            'theme_pack_editorial entitlement must grant access to Noir'
        );
    }

    public function test_editorial_entitlement_does_not_grant_atelier(): void
    {
        $agency = $this->makeAgency();
        $this->grantEntitlement($agency, PremiumThemePackServiceProvider::FEATURE_CODE_EDITORIAL);

        $this->assertFalse(
            $this->service()->canUseFeature($agency, $this->featureCodeFor('atelier')),
            'theme_pack_editorial entitlement must NOT grant access to Atelier'
        );
    }

    public function test_editorial_entitlement_does_not_grant_meridian(): void
    {
        $agency = $this->makeAgency();
        $this->grantEntitlement($agency, PremiumThemePackServiceProvider::FEATURE_CODE_EDITORIAL);

        $this->assertFalse(
            $this->service()->canUseFeature($agency, $this->featureCodeFor('meridian')),
            'theme_pack_editorial entitlement must NOT grant access to Meridian'
        );
    }

    // ── 5-8. Business SKU grants Atelier + Meridian only ─────────────────────

    public function test_business_entitlement_grants_atelier(): void
    {
        $agency = $this->makeAgency();
        $this->grantEntitlement($agency, PremiumThemePackServiceProvider::FEATURE_CODE_BUSINESS);

        $this->assertTrue(
            $this->service()->canUseFeature($agency, $this->featureCodeFor('atelier')),
            'theme_pack_business entitlement must grant access to Atelier'
        );
    }

    public function test_business_entitlement_grants_meridian(): void
    {
        $agency = $this->makeAgency();
        $this->grantEntitlement($agency, PremiumThemePackServiceProvider::FEATURE_CODE_BUSINESS);

        $this->assertTrue(
            $this->service()->canUseFeature($agency, $this->featureCodeFor('meridian')),
            'theme_pack_business entitlement must grant access to Meridian'
        );
    }

    public function test_business_entitlement_does_not_grant_midnight(): void
    {
        $agency = $this->makeAgency();
        $this->grantEntitlement($agency, PremiumThemePackServiceProvider::FEATURE_CODE_BUSINESS);

        $this->assertFalse(
            $this->service()->canUseFeature($agency, $this->featureCodeFor('midnight')),
            'theme_pack_business entitlement must NOT grant access to Midnight'
        );
    }

    public function test_business_entitlement_does_not_grant_noir(): void
    {
        $agency = $this->makeAgency();
        $this->grantEntitlement($agency, PremiumThemePackServiceProvider::FEATURE_CODE_BUSINESS);

        $this->assertFalse(
            $this->service()->canUseFeature($agency, $this->featureCodeFor('noir')),
            'theme_pack_business entitlement must NOT grant access to Noir'
        );
    }

    // ── 9. Legacy theme_premium entitlement grants all 4 premium themes ───────

    public function test_legacy_theme_premium_entitlement_grants_all_premium_themes(): void
    {
        $agency = $this->makeAgency();
        $this->grantEntitlement($agency, PremiumThemePackServiceProvider::FEATURE_CODE_LEGACY);

        foreach (['midnight', 'noir', 'atelier', 'meridian'] as $slug) {
            $code = $this->featureCodeFor($slug);
            $this->assertTrue(
                $this->service()->canUseFeature($agency, $code),
                "Legacy theme_premium entitlement must grant access to {$slug} (featureCode: {$code})"
            );
        }
    }

    // ── 10. Legacy theme_premium plan grants all 4 premium themes ────────────

    public function test_legacy_theme_premium_plan_grants_all_premium_themes(): void
    {
        $plan = $this->makePlanWithFeature(PremiumThemePackServiceProvider::FEATURE_CODE_LEGACY);
        $agency = $this->makeAgency($plan);

        foreach (['midnight', 'noir', 'atelier', 'meridian'] as $slug) {
            $code = $this->featureCodeFor($slug);
            $this->assertTrue(
                $this->service()->canUseFeature($agency, $code),
                "Legacy theme_premium plan must grant access to {$slug} (featureCode: {$code})"
            );
        }
    }

    // ── 11. PremiumPackConfig has correct per-SKU theme lists ─────────────────

    public function test_premium_pack_config_has_correct_sku_theme_lists(): void
    {
        $editorial = PremiumPackConfig::forCode(PremiumThemePackServiceProvider::FEATURE_CODE_EDITORIAL);
        $business = PremiumPackConfig::forCode(PremiumThemePackServiceProvider::FEATURE_CODE_BUSINESS);

        $this->assertNotNull($editorial, 'Editorial pack must exist in PremiumPackConfig');
        $this->assertNotNull($business, 'Business pack must exist in PremiumPackConfig');

        $this->assertContains('Midnight', $editorial['includes']);
        $this->assertContains('Noir', $editorial['includes']);
        $this->assertNotContains('Atelier', $editorial['includes']);
        $this->assertNotContains('Meridian', $editorial['includes']);

        $this->assertContains('Atelier', $business['includes']);
        $this->assertContains('Meridian', $business['includes']);
        $this->assertNotContains('Midnight', $business['includes']);
        $this->assertNotContains('Noir', $business['includes']);
    }

    // ── 12. unavailableFor() with editorial entitlement ──────────────────────

    public function test_unavailable_for_with_editorial_entitlement_shows_business_as_unavailable(): void
    {
        $agency = $this->makeAgency();
        $this->grantEntitlement($agency, PremiumThemePackServiceProvider::FEATURE_CODE_EDITORIAL);

        $unavailable = PremiumPackConfig::unavailableFor($agency);
        $codes = array_column($unavailable, 'featureCode');

        $this->assertNotContains(PremiumThemePackServiceProvider::FEATURE_CODE_EDITORIAL, $codes);
        $this->assertContains(PremiumThemePackServiceProvider::FEATURE_CODE_BUSINESS, $codes);
    }

    // ── 13. unavailableFor() with legacy theme_premium excludes all theme packs

    public function test_unavailable_for_with_legacy_entitlement_excludes_all_theme_packs(): void
    {
        $agency = $this->makeAgency();
        $this->grantEntitlement($agency, PremiumThemePackServiceProvider::FEATURE_CODE_LEGACY);

        $unavailable = PremiumPackConfig::unavailableFor($agency);
        $codes = array_column($unavailable, 'featureCode');

        $this->assertNotContains(PremiumThemePackServiceProvider::FEATURE_CODE_EDITORIAL, $codes);
        $this->assertNotContains(PremiumThemePackServiceProvider::FEATURE_CODE_BUSINESS, $codes);
        // block_pack_marketing remains unavailable (legacy doesn't cover it)
        $this->assertContains('block_pack_marketing', $codes);
    }

    // ── 14. unavailableFor() with both theme packs ────────────────────────────

    public function test_unavailable_for_with_both_theme_pack_entitlements_excludes_all_theme_packs(): void
    {
        $agency = $this->makeAgency();
        $this->grantEntitlement($agency, PremiumThemePackServiceProvider::FEATURE_CODE_EDITORIAL);
        $this->grantEntitlement($agency, PremiumThemePackServiceProvider::FEATURE_CODE_BUSINESS);

        $unavailable = PremiumPackConfig::unavailableFor($agency);
        $codes = array_column($unavailable, 'featureCode');

        $this->assertNotContains(PremiumThemePackServiceProvider::FEATURE_CODE_EDITORIAL, $codes);
        $this->assertNotContains(PremiumThemePackServiceProvider::FEATURE_CODE_BUSINESS, $codes);
        // Only block_pack remains unavailable
        $this->assertCount(1, $unavailable);
        $this->assertSame('block_pack_marketing', $codes[0]);
    }
}
