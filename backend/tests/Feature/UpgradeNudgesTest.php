<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Filament\Agency\Widgets\ThemePremiumNudgeWidget;
use App\Models\Central\Agency;
use App\Models\Central\AgencyEntitlement;
use App\Models\Central\Plan;
use App\Models\Central\PluginCatalogItem;
use App\Services\PremiumPackConfig;
use Tests\CentralTestCase;

/**
 * Upgrade Nudges — Fase 4A/4C test suite.
 *
 * Tests:
 *  1.  PremiumPackConfig::all() returns exactly three packs (post Fase 4C SKU split)
 *  2.  Theme Pack Editorial has the expected structure and fields (Midnight + Noir)
 *  3.  Marketing block pack has the expected structure and fields
 *  4.  PremiumPackConfig::forCode() returns the correct pack for theme_pack_editorial
 *  5.  PremiumPackConfig::forCode() returns null for an unknown code
 *  6.  PremiumPackConfig::unavailableFor(null) returns all packs
 *  7.  PremiumPackConfig::unavailableFor() with no entitlements returns all packs
 *  8.  PremiumPackConfig::unavailableFor() with editorial entitlement removes editorial from unavailable
 *  9.  PremiumPackConfig::unavailableFor() with all entitlements returns empty array
 * 10.  ThemePremiumNudgeWidget::canView() returns false when no agency is bound
 * 11.  ThemePremiumNudgeWidget::canView() returns true when agency lacks any premium theme pack
 * 12.  ThemePremiumNudgeWidget::canView() returns false when agency has legacy theme_premium via entitlement
 * 13.  ThemePremiumNudgeWidget::canView() returns false when agency has legacy theme_premium via plan
 */
class UpgradeNudgesTest extends CentralTestCase
{
    private static int $seq = 0;

    // ── Helpers ───────────────────────────────────────────────────────────────

    private function makeAgency(?Plan $plan = null): Agency
    {
        self::$seq++;

        return Agency::create([
            'name' => 'Agency Nudge '.self::$seq,
            'slug' => 'agency-nudge-'.self::$seq,
            'brand_name' => 'Agency Nudge '.self::$seq,
            'status' => 'active',
            'billing_type' => 'monthly',
            'plan_id' => $plan?->id,
        ]);
    }

    private function makePlanWithFeature(string $featureCode): Plan
    {
        self::$seq++;

        return Plan::create([
            'name' => 'Plan Nudge '.self::$seq,
            'slug' => 'plan-nudge-'.self::$seq,
            'price' => 99,
            'billing_interval' => 'month',
            'features' => [],
            'limits' => [$featureCode => true],
            'is_active' => true,
        ]);
    }

    private function makeCatalogItem(string $code, string $type = PluginCatalogItem::TYPE_THEME_PACK): PluginCatalogItem
    {
        return PluginCatalogItem::create([
            'code' => $code,
            'type' => $type,
            'name' => ucfirst(str_replace('_', ' ', $code)),
            'status' => PluginCatalogItem::STATUS_ACTIVE,
        ]);
    }

    private function grantEntitlement(Agency $agency, PluginCatalogItem $item): AgencyEntitlement
    {
        return AgencyEntitlement::create([
            'agency_id' => $agency->id,
            'catalog_item_id' => $item->id,
            'source' => AgencyEntitlement::SOURCE_MANUAL,
            'status' => AgencyEntitlement::STATUS_ACTIVE,
        ]);
    }

    // ── 1. PremiumPackConfig::all() ───────────────────────────────────────────

    public function test_premium_pack_config_returns_exactly_three_packs(): void
    {
        $packs = PremiumPackConfig::all();

        $this->assertCount(3, $packs);
    }

    // ── 2. Theme Pack Editorial structure ────────────────────────────────────

    public function test_theme_pack_editorial_has_expected_structure(): void
    {
        $pack = PremiumPackConfig::forCode('theme_pack_editorial');

        $this->assertNotNull($pack);
        $this->assertSame('theme_pack_editorial', $pack['featureCode']);
        $this->assertSame('theme_pack', $pack['type']);
        $this->assertNotEmpty($pack['label']);
        $this->assertNotEmpty($pack['description']);
        $this->assertNotEmpty($pack['ctaLabel']);
        $this->assertContains('Midnight', $pack['includes']);
        $this->assertContains('Noir', $pack['includes']);
        $this->assertNotContains('Atelier', $pack['includes']);
        $this->assertNotContains('Meridian', $pack['includes']);
    }

    // ── 3. Block pack structure ───────────────────────────────────────────────

    public function test_block_pack_marketing_has_expected_structure(): void
    {
        $pack = PremiumPackConfig::forCode('block_pack_marketing');

        $this->assertNotNull($pack);
        $this->assertSame('block_pack_marketing', $pack['featureCode']);
        $this->assertSame('block_pack', $pack['type']);
        $this->assertNotEmpty($pack['label']);
        $this->assertNotEmpty($pack['description']);
        $this->assertNotEmpty($pack['ctaLabel']);
        $this->assertContains('Pricing Table', $pack['includes']);
        $this->assertContains('Logo Cloud', $pack['includes']);
        $this->assertContains('Stats Strip', $pack['includes']);
        $this->assertContains('Testimonial Carousel', $pack['includes']);
        $this->assertContains('CTA Split', $pack['includes']);
    }

    // ── 4. forCode() hit ─────────────────────────────────────────────────────

    public function test_for_code_returns_matching_pack(): void
    {
        $pack = PremiumPackConfig::forCode('theme_pack_editorial');

        $this->assertIsArray($pack);
        $this->assertSame('theme_pack_editorial', $pack['featureCode']);
    }

    // ── 5. forCode() miss ─────────────────────────────────────────────────────

    public function test_for_code_returns_null_for_unknown_code(): void
    {
        $this->assertNull(PremiumPackConfig::forCode('nonexistent_code'));
    }

    // ── 6. unavailableFor(null) ───────────────────────────────────────────────

    public function test_unavailable_for_null_returns_all_packs(): void
    {
        $packs = PremiumPackConfig::unavailableFor(null);

        $this->assertCount(3, $packs);
    }

    // ── 7. unavailableFor() — no entitlements ────────────────────────────────

    public function test_unavailable_for_agency_without_entitlements_returns_all_packs(): void
    {
        $agency = $this->makeAgency();

        $packs = PremiumPackConfig::unavailableFor($agency);

        $this->assertCount(3, $packs);
        $codes = array_column($packs, 'featureCode');
        $this->assertContains('theme_pack_editorial', $codes);
        $this->assertContains('theme_pack_business', $codes);
        $this->assertContains('block_pack_marketing', $codes);
    }

    // ── 8. unavailableFor() — editorial entitlement removes editorial ─────────

    public function test_unavailable_for_agency_with_editorial_entitlement_returns_remaining_packs(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem('theme_pack_editorial', PluginCatalogItem::TYPE_THEME_PACK);
        $this->grantEntitlement($agency, $item);

        $packs = PremiumPackConfig::unavailableFor($agency);

        $this->assertCount(2, $packs);
        $codes = array_column($packs, 'featureCode');
        $this->assertNotContains('theme_pack_editorial', $codes);
        $this->assertContains('theme_pack_business', $codes);
        $this->assertContains('block_pack_marketing', $codes);
    }

    // ── 9. unavailableFor() — all entitlements ───────────────────────────────

    public function test_unavailable_for_agency_with_all_entitlements_returns_empty(): void
    {
        $agency = $this->makeAgency();
        $editorialItem = $this->makeCatalogItem('theme_pack_editorial', PluginCatalogItem::TYPE_THEME_PACK);
        $businessItem = $this->makeCatalogItem('theme_pack_business', PluginCatalogItem::TYPE_THEME_PACK);
        $blockItem = $this->makeCatalogItem('block_pack_marketing', PluginCatalogItem::TYPE_BLOCK_PACK);
        $this->grantEntitlement($agency, $editorialItem);
        $this->grantEntitlement($agency, $businessItem);
        $this->grantEntitlement($agency, $blockItem);

        $packs = PremiumPackConfig::unavailableFor($agency);

        $this->assertEmpty($packs);
    }

    // ── 10. Widget hidden when no agency ──────────────────────────────────────

    public function test_theme_premium_nudge_widget_hidden_when_no_agency(): void
    {
        // No agency bound — canView() must return false to avoid rendering errors.
        app()->forgetInstance('current_agency');

        $this->assertFalse(ThemePremiumNudgeWidget::canView());
    }

    // ── 11. Widget visible when agency lacks any premium theme pack ───────────

    public function test_theme_premium_nudge_widget_visible_when_no_theme_pack_entitlement(): void
    {
        $agency = $this->makeAgency();
        app()->instance('current_agency', $agency);

        $this->assertTrue(ThemePremiumNudgeWidget::canView());
    }

    // ── 12. Widget hidden when agency has theme_premium via entitlement ───────

    public function test_theme_premium_nudge_widget_hidden_when_agency_has_theme_premium_entitlement(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem('theme_premium', PluginCatalogItem::TYPE_THEME_PACK);
        $this->grantEntitlement($agency, $item);

        app()->instance('current_agency', $agency);

        $this->assertFalse(ThemePremiumNudgeWidget::canView());
    }

    // ── 13. Widget hidden when agency has theme_premium via plan ──────────────

    public function test_theme_premium_nudge_widget_hidden_when_agency_has_theme_premium_via_plan(): void
    {
        $plan = $this->makePlanWithFeature('theme_premium');
        $agency = $this->makeAgency($plan);

        app()->instance('current_agency', $agency);

        $this->assertFalse(ThemePremiumNudgeWidget::canView());
    }

    // ── Teardown: clear agency instance so tests don't bleed ──────────────────

    protected function tearDown(): void
    {
        app()->forgetInstance('current_agency');
        parent::tearDown();
    }
}
