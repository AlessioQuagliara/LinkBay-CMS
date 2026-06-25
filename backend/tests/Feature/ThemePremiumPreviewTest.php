<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Filament\Agency\Resources\ThemePresetResource;
use App\Models\Central\Agency;
use App\Models\Central\AgencyEntitlement;
use App\Models\Central\Plan;
use App\Models\Central\PluginCatalogItem;
use App\Models\Central\ThemePreset;
use App\Services\ThemeConfigSchema;
use Tests\CentralTestCase;

/**
 * Theme Premium Preview Mode — Fase 4B test suite.
 *
 * Tests:
 *  1.  Premium theme is visible in list even without entitlement (preview mode)
 *  2.  Premium theme is visible in list with entitlement
 *  3.  Free system theme always visible regardless of entitlements
 *  4.  Agency-owned theme always visible (regression)
 *  5.  isPremiumPreview() returns true for premium theme without entitlement
 *  6.  isPremiumPreview() returns false for premium theme with entitlement
 *  7.  isPremiumPreview() returns false for free system theme
 *  8.  isPremiumPreview() returns false for agency-owned (non-system) theme
 *  9.  isPremiumPreview() returns true when no agency context is bound
 * 10.  Other agency's premium entitlement does not bleed across (isolation)
 * 11.  Premium theme with plan-based access is not in preview mode
 */
class ThemePremiumPreviewTest extends CentralTestCase
{
    private static int $seq = 0;

    // ── Helpers ───────────────────────────────────────────────────────────────

    private function makeAgency(?Plan $plan = null): Agency
    {
        self::$seq++;

        return Agency::create([
            'name' => 'Preview Agency '.self::$seq,
            'slug' => 'preview-agency-'.self::$seq,
            'brand_name' => 'Preview Agency '.self::$seq,
            'status' => 'active',
            'billing_type' => 'monthly',
            'plan_id' => $plan?->id,
        ]);
    }

    private function makePremiumSystemPreset(string $slug = 'noir'): ThemePreset
    {
        // slug must match a theme registered with featureCode in the PluginRegistry
        // (noir / atelier / meridian / midnight — all registered by PremiumThemePackServiceProvider)
        return ThemePreset::create([
            'agency_id' => null,
            'name' => ucfirst($slug),
            'slug' => $slug,
            'status' => ThemePreset::STATUS_ACTIVE,
            'is_system' => true,
            'config' => ThemeConfigSchema::defaults(),
        ]);
    }

    private function makeFreeSystemPreset(): ThemePreset
    {
        // 'ocean' is registered in CoreThemesServiceProvider with featureCode = null
        self::$seq++;

        return ThemePreset::create([
            'agency_id' => null,
            'name' => 'Ocean '.self::$seq,
            'slug' => 'ocean',
            'status' => ThemePreset::STATUS_ACTIVE,
            'is_system' => true,
            'config' => ThemeConfigSchema::defaults(),
        ]);
    }

    private function makeAgencyPreset(Agency $agency): ThemePreset
    {
        self::$seq++;

        return ThemePreset::create([
            'agency_id' => $agency->id,
            'name' => 'Custom '.self::$seq,
            'slug' => 'custom-'.self::$seq,
            'status' => ThemePreset::STATUS_DRAFT,
            'is_system' => false,
            'config' => ThemeConfigSchema::defaults(),
        ]);
    }

    private function makeCatalogItem(string $code): PluginCatalogItem
    {
        return PluginCatalogItem::create([
            'code' => $code,
            'type' => PluginCatalogItem::TYPE_THEME_PACK,
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

    private function makePlanWithFeature(string $code): Plan
    {
        self::$seq++;

        return Plan::create([
            'name' => 'Plan Preview '.self::$seq,
            'slug' => 'plan-preview-'.self::$seq,
            'price' => 99,
            'billing_interval' => 'month',
            'features' => [],
            'limits' => [$code => true],
            'is_active' => true,
        ]);
    }

    // ── 1. Premium theme visible without entitlement ──────────────────────────

    public function test_premium_theme_visible_in_list_without_entitlement(): void
    {
        $agency = $this->makeAgency();
        $preset = $this->makePremiumSystemPreset('noir');

        app()->instance('current_agency', $agency);

        $results = ThemePresetResource::getEloquentQuery()->get();

        $this->assertTrue($results->contains('id', $preset->id));
    }

    // ── 2. Premium theme visible with entitlement ─────────────────────────────

    public function test_premium_theme_visible_in_list_with_entitlement(): void
    {
        $agency = $this->makeAgency();
        $preset = $this->makePremiumSystemPreset('atelier');
        $item = $this->makeCatalogItem('theme_premium');
        $this->grantEntitlement($agency, $item);

        app()->instance('current_agency', $agency);

        $results = ThemePresetResource::getEloquentQuery()->get();

        $this->assertTrue($results->contains('id', $preset->id));
    }

    // ── 3. Free system theme always visible ───────────────────────────────────

    public function test_free_system_theme_always_visible_without_entitlement(): void
    {
        $agency = $this->makeAgency();
        $preset = $this->makeFreeSystemPreset();

        app()->instance('current_agency', $agency);

        $results = ThemePresetResource::getEloquentQuery()->get();

        $this->assertTrue($results->contains('id', $preset->id));
    }

    // ── 4. Agency-owned theme visible (regression) ────────────────────────────

    public function test_agency_owned_theme_always_visible(): void
    {
        $agency = $this->makeAgency();
        $preset = $this->makeAgencyPreset($agency);

        app()->instance('current_agency', $agency);

        $results = ThemePresetResource::getEloquentQuery()->get();

        $this->assertTrue($results->contains('id', $preset->id));
    }

    // ── 5. isPremiumPreview true without entitlement ──────────────────────────

    public function test_is_premium_preview_true_when_no_entitlement(): void
    {
        $agency = $this->makeAgency();
        $preset = $this->makePremiumSystemPreset('noir');

        app()->instance('current_agency', $agency);

        $this->assertTrue(ThemePresetResource::isPremiumPreview($preset));
    }

    // ── 6. isPremiumPreview false with entitlement ────────────────────────────

    public function test_is_premium_preview_false_when_entitlement_active(): void
    {
        $agency = $this->makeAgency();
        $preset = $this->makePremiumSystemPreset('meridian');
        $item = $this->makeCatalogItem('theme_premium');
        $this->grantEntitlement($agency, $item);

        app()->instance('current_agency', $agency);

        $this->assertFalse(ThemePresetResource::isPremiumPreview($preset));
    }

    // ── 7. isPremiumPreview false for free system theme ───────────────────────

    public function test_is_premium_preview_false_for_free_system_theme(): void
    {
        $agency = $this->makeAgency();
        $preset = $this->makeFreeSystemPreset();

        app()->instance('current_agency', $agency);

        $this->assertFalse(ThemePresetResource::isPremiumPreview($preset));
    }

    // ── 8. isPremiumPreview false for agency-owned theme ─────────────────────

    public function test_is_premium_preview_false_for_agency_theme(): void
    {
        $agency = $this->makeAgency();
        $preset = $this->makeAgencyPreset($agency);

        app()->instance('current_agency', $agency);

        $this->assertFalse(ThemePresetResource::isPremiumPreview($preset));
    }

    // ── 9. isPremiumPreview true when no agency context bound ─────────────────

    public function test_is_premium_preview_true_when_no_agency_bound(): void
    {
        $preset = $this->makePremiumSystemPreset('noir');

        app()->forgetInstance('current_agency');

        $this->assertTrue(ThemePresetResource::isPremiumPreview($preset));
    }

    // ── 10. Cross-agency isolation ────────────────────────────────────────────

    public function test_entitlement_of_other_agency_does_not_grant_preview_access(): void
    {
        $agencyA = $this->makeAgency();
        $agencyB = $this->makeAgency();
        $preset = $this->makePremiumSystemPreset('atelier');
        $item = $this->makeCatalogItem('theme_premium');

        // Only agency B gets the entitlement
        $this->grantEntitlement($agencyB, $item);

        // Bind agency A — should still be in preview mode
        app()->instance('current_agency', $agencyA);

        $this->assertTrue(ThemePresetResource::isPremiumPreview($preset));
    }

    // ── 11. Plan-based access removes preview mode ────────────────────────────

    public function test_is_premium_preview_false_when_access_via_plan(): void
    {
        $plan = $this->makePlanWithFeature('theme_premium');
        $agency = $this->makeAgency($plan);
        $preset = $this->makePremiumSystemPreset('noir');

        app()->instance('current_agency', $agency);

        $this->assertFalse(ThemePresetResource::isPremiumPreview($preset));
    }

    // ── Teardown ──────────────────────────────────────────────────────────────

    protected function tearDown(): void
    {
        app()->forgetInstance('current_agency');
        parent::tearDown();
    }
}
