<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\Agency;
use App\Models\Central\AgencyEntitlement;
use App\Models\Central\LayoutAssignment;
use App\Models\Central\LayoutTemplate;
use App\Models\Central\Plan;
use App\Models\Central\PluginCatalogItem;
use App\Models\Central\ThemeAssignment;
use App\Models\Central\ThemePreset;
use App\Plugins\MarketingBlockPack\MarketingBlockPackServiceProvider;
use App\Services\LayoutRendererService;
use App\Services\ThemeConfigSchema;
use Illuminate\Support\Facades\DB;
use Tests\CentralTestCase;

/**
 * Storefront premium enforcement test suite.
 *
 * Tests that LayoutRendererService::renderStorefront() applies feature-access
 * enforcement consistently with FeatureAccessService and PluginRegistry.
 *
 * Tests:
 *  1.  Free blocks are always included in the storefront payload
 *  2.  Premium block rendered when agency has active entitlement
 *  3.  Premium block excluded when agency has no entitlement
 *  4.  Premium block excluded when entitlement is revoked
 *  5.  Premium block visible when granted via plan limits
 *  6.  Free system theme is always served (no gate)
 *  7.  Premium system theme served when agency has entitlement
 *  8.  Premium system theme falls back to defaults when no entitlement
 *  9.  Premium system theme falls back to defaults when entitlement revoked
 * 10.  Custom (non-system) theme preset is always served regardless of featureCode
 * 11.  renderStorefront() returns null when no layout assignment exists
 * 12.  Payload is always structurally valid (theme + blocks keys present)
 * 13.  Cross-tenant scoping: agency A entitlement does not affect agency B tenant
 */
class StorefrontPremiumEnforcementTest extends CentralTestCase
{
    private static int $seq = 0;

    // ── Helpers ───────────────────────────────────────────────────────────────

    private function renderer(): LayoutRendererService
    {
        return app(LayoutRendererService::class);
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

    /** Raw insert to avoid stancl/tenancy DB-provisioning hooks. */
    private function makeTenant(Agency $agency): string
    {
        self::$seq++;
        $id = 'store-'.self::$seq;

        DB::connection('central')->table('tenants')->insert([
            'id' => $id,
            'name' => 'Store '.self::$seq,
            'status' => 'active',
            'agency_id' => $agency->id,
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        return $id;
    }

    private function makeTemplate(Agency $agency, array $blocks = []): LayoutTemplate
    {
        self::$seq++;

        return LayoutTemplate::create([
            'agency_id' => $agency->id,
            'name' => 'Template '.self::$seq,
            'slug' => 'template-'.self::$seq,
            'status' => LayoutTemplate::STATUS_PUBLISHED,
            'blocks' => $blocks,
        ]);
    }

    private function assignLayout(Agency $agency, string $tenantId, LayoutTemplate $template, string $page = 'home'): void
    {
        LayoutAssignment::create([
            'agency_id' => $agency->id,
            'tenant_id' => $tenantId,
            'layout_template_id' => $template->id,
            'page_key' => $page,
        ]);
    }

    private function makeSystemThemePreset(Agency $agency, string $slug, array $config = []): ThemePreset
    {
        self::$seq++;

        return ThemePreset::create([
            'agency_id' => $agency->id,
            'name' => ucfirst($slug).' '.self::$seq,
            'slug' => $slug,
            'status' => ThemePreset::STATUS_ACTIVE,
            'is_system' => true,
            'config' => $config ?: ThemeConfigSchema::defaults(),
        ]);
    }

    private function makeCustomThemePreset(Agency $agency): ThemePreset
    {
        self::$seq++;

        return ThemePreset::create([
            'agency_id' => $agency->id,
            'name' => 'Custom Theme '.self::$seq,
            'slug' => 'custom-theme-'.self::$seq,
            'status' => ThemePreset::STATUS_ACTIVE,
            'is_system' => false,
            'config' => ThemeConfigSchema::defaults(),
        ]);
    }

    private function assignTheme(Agency $agency, string $tenantId, ThemePreset $preset): void
    {
        ThemeAssignment::create([
            'agency_id' => $agency->id,
            'tenant_id' => $tenantId,
            'theme_preset_id' => $preset->id,
        ]);
    }

    private function grantEntitlement(Agency $agency, string $featureCode, string $status = AgencyEntitlement::STATUS_ACTIVE): void
    {
        $item = PluginCatalogItem::firstOrCreate(
            ['code' => $featureCode],
            [
                'type' => PluginCatalogItem::TYPE_BLOCK_PACK,
                'name' => ucwords(str_replace('_', ' ', $featureCode)),
                'status' => PluginCatalogItem::STATUS_ACTIVE,
            ]
        );

        AgencyEntitlement::create([
            'agency_id' => $agency->id,
            'catalog_item_id' => $item->id,
            'source' => AgencyEntitlement::SOURCE_MANUAL,
            'status' => $status,
        ]);
    }

    private function freeBlock(string $type = 'hero'): array
    {
        return ['type' => $type, 'data' => ['title' => 'Hello', 'subtitle' => 'World']];
    }

    private function premiumBlock(): array
    {
        // pricing_table is registered by MarketingBlockPackServiceProvider
        return ['type' => 'pricing_table', 'data' => ['tiers' => []]];
    }

    // ── 1. Free blocks always included ───────────────────────────────────────

    public function test_free_blocks_are_always_included(): void
    {
        $agency = $this->makeAgency(); // no plan, no entitlements
        $tenantId = $this->makeTenant($agency);
        $template = $this->makeTemplate($agency, [$this->freeBlock('hero'), $this->freeBlock('cta')]);
        $this->assignLayout($agency, $tenantId, $template);

        $payload = $this->renderer()->renderStorefront($tenantId, 'home');

        $this->assertNotNull($payload);
        $types = array_column($payload['blocks'], 'type');
        $this->assertContains('hero', $types);
        $this->assertContains('cta', $types);
    }

    // ── 2. Premium block rendered with entitlement ────────────────────────────

    public function test_premium_block_is_rendered_with_active_entitlement(): void
    {
        $agency = $this->makeAgency();
        $this->grantEntitlement($agency, MarketingBlockPackServiceProvider::FEATURE_CODE);

        $tenantId = $this->makeTenant($agency);
        $template = $this->makeTemplate($agency, [$this->freeBlock(), $this->premiumBlock()]);
        $this->assignLayout($agency, $tenantId, $template);

        $payload = $this->renderer()->renderStorefront($tenantId, 'home');

        $types = array_column($payload['blocks'], 'type');
        $this->assertContains('pricing_table', $types);
    }

    // ── 3. Premium block excluded without entitlement ────────────────────────

    public function test_premium_block_excluded_without_entitlement(): void
    {
        $agency = $this->makeAgency(); // no entitlement
        $tenantId = $this->makeTenant($agency);
        $template = $this->makeTemplate($agency, [$this->freeBlock(), $this->premiumBlock()]);
        $this->assignLayout($agency, $tenantId, $template);

        $payload = $this->renderer()->renderStorefront($tenantId, 'home');

        $types = array_column($payload['blocks'], 'type');
        $this->assertNotContains('pricing_table', $types);
        $this->assertContains('hero', $types); // free block still present
    }

    // ── 4. Premium block excluded when entitlement revoked ────────────────────

    public function test_premium_block_excluded_when_entitlement_revoked(): void
    {
        $agency = $this->makeAgency();
        $this->grantEntitlement($agency, MarketingBlockPackServiceProvider::FEATURE_CODE, AgencyEntitlement::STATUS_REVOKED);

        $tenantId = $this->makeTenant($agency);
        $template = $this->makeTemplate($agency, [$this->premiumBlock()]);
        $this->assignLayout($agency, $tenantId, $template);

        $payload = $this->renderer()->renderStorefront($tenantId, 'home');

        $this->assertEmpty($payload['blocks']);
    }

    // ── 5. Premium block rendered when granted via plan ───────────────────────

    public function test_premium_block_rendered_when_granted_via_plan(): void
    {
        $plan = $this->makePlan([MarketingBlockPackServiceProvider::FEATURE_CODE => true]);
        $agency = $this->makeAgency($plan);

        $tenantId = $this->makeTenant($agency);
        $template = $this->makeTemplate($agency, [$this->premiumBlock()]);
        $this->assignLayout($agency, $tenantId, $template);

        $payload = $this->renderer()->renderStorefront($tenantId, 'home');

        $types = array_column($payload['blocks'], 'type');
        $this->assertContains('pricing_table', $types);
    }

    // ── 6. Free system theme always served ────────────────────────────────────

    public function test_free_system_theme_is_always_served(): void
    {
        $agency = $this->makeAgency(); // no premium access
        $tenantId = $this->makeTenant($agency);
        $template = $this->makeTemplate($agency, [$this->freeBlock()]);
        $this->assignLayout($agency, $tenantId, $template);

        // 'ocean' is a free system theme (no featureCode)
        $oceanPreset = $this->makeSystemThemePreset($agency, 'ocean');
        $this->assignTheme($agency, $tenantId, $oceanPreset);

        $payload = $this->renderer()->renderStorefront($tenantId, 'home');

        $this->assertNotNull($payload);
        $this->assertArrayHasKey('palette', $payload['theme']);
    }

    // ── 7. Premium system theme served with entitlement ───────────────────────

    public function test_premium_system_theme_served_with_active_entitlement(): void
    {
        $agency = $this->makeAgency();
        $this->grantEntitlement($agency, 'theme_premium');

        $tenantId = $this->makeTenant($agency);
        $template = $this->makeTemplate($agency, [$this->freeBlock()]);
        $this->assignLayout($agency, $tenantId, $template);

        // 'midnight' requires theme_premium
        $midnightConfig = ['palette' => ['primary' => '#818cf8', 'secondary' => '#1e293b', 'accent' => '#f59e0b', 'surface' => '#0f172a', 'text' => '#f8fafc']];
        $midnight = $this->makeSystemThemePreset($agency, 'midnight', $midnightConfig);
        $this->assignTheme($agency, $tenantId, $midnight);

        $payload = $this->renderer()->renderStorefront($tenantId, 'home');

        // Should serve the midnight palette, not the default primary
        $this->assertEquals('#818cf8', $payload['theme']['palette']['primary']);
    }

    // ── 8. Premium system theme falls back when no entitlement ───────────────

    public function test_premium_system_theme_falls_back_to_defaults_without_entitlement(): void
    {
        $agency = $this->makeAgency(); // no premium
        $tenantId = $this->makeTenant($agency);
        $template = $this->makeTemplate($agency, [$this->freeBlock()]);
        $this->assignLayout($agency, $tenantId, $template);

        $midnightConfig = ['palette' => ['primary' => '#818cf8', 'secondary' => '#1e293b', 'accent' => '#f59e0b', 'surface' => '#0f172a', 'text' => '#f8fafc']];
        $midnight = $this->makeSystemThemePreset($agency, 'midnight', $midnightConfig);
        $this->assignTheme($agency, $tenantId, $midnight);

        $payload = $this->renderer()->renderStorefront($tenantId, 'home');

        $defaults = ThemeConfigSchema::defaults();
        $this->assertEquals($defaults['palette']['primary'], $payload['theme']['palette']['primary']);
    }

    // ── 9. Premium theme falls back when entitlement revoked ─────────────────

    public function test_premium_system_theme_falls_back_when_entitlement_revoked(): void
    {
        $agency = $this->makeAgency();
        $this->grantEntitlement($agency, 'theme_premium', AgencyEntitlement::STATUS_REVOKED);

        $tenantId = $this->makeTenant($agency);
        $template = $this->makeTemplate($agency, [$this->freeBlock()]);
        $this->assignLayout($agency, $tenantId, $template);

        $midnightConfig = ['palette' => ['primary' => '#818cf8', 'secondary' => '#1e293b', 'accent' => '#f59e0b', 'surface' => '#0f172a', 'text' => '#f8fafc']];
        $midnight = $this->makeSystemThemePreset($agency, 'midnight', $midnightConfig);
        $this->assignTheme($agency, $tenantId, $midnight);

        $payload = $this->renderer()->renderStorefront($tenantId, 'home');

        $defaults = ThemeConfigSchema::defaults();
        $this->assertEquals($defaults['palette']['primary'], $payload['theme']['palette']['primary']);
    }

    // ── 10. Custom preset always served ──────────────────────────────────────

    public function test_custom_theme_preset_always_served_regardless_of_feature_access(): void
    {
        $agency = $this->makeAgency(); // no premium
        $tenantId = $this->makeTenant($agency);
        $template = $this->makeTemplate($agency, [$this->freeBlock()]);
        $this->assignLayout($agency, $tenantId, $template);

        $custom = $this->makeCustomThemePreset($agency);
        $this->assignTheme($agency, $tenantId, $custom);

        $payload = $this->renderer()->renderStorefront($tenantId, 'home');

        $this->assertNotNull($payload);
        $this->assertArrayHasKey('palette', $payload['theme']);
    }

    // ── 11. null when no layout assignment ───────────────────────────────────

    public function test_returns_null_when_no_layout_assignment(): void
    {
        $agency = $this->makeAgency();
        $tenantId = $this->makeTenant($agency);

        $this->assertNull($this->renderer()->renderStorefront($tenantId, 'home'));
    }

    // ── 12. Payload always structurally valid ─────────────────────────────────

    public function test_payload_is_always_structurally_valid(): void
    {
        $agency = $this->makeAgency(); // nothing configured
        $tenantId = $this->makeTenant($agency);
        $template = $this->makeTemplate($agency, [$this->premiumBlock()]); // only premium blocks
        $this->assignLayout($agency, $tenantId, $template);

        $payload = $this->renderer()->renderStorefront($tenantId, 'home');

        $this->assertNotNull($payload);
        $this->assertArrayHasKey('theme', $payload);
        $this->assertArrayHasKey('blocks', $payload);
        $this->assertIsArray($payload['theme']);
        $this->assertIsArray($payload['blocks']);
        // All premium blocks excluded, but payload is still valid with empty blocks
        $this->assertEmpty($payload['blocks']);
        // Theme falls back to defaults
        $this->assertArrayHasKey('palette', $payload['theme']);
    }

    // ── 13. Cross-tenant scoping ──────────────────────────────────────────────

    public function test_cross_tenant_feature_access_does_not_bleed(): void
    {
        $agencyA = $this->makeAgency();
        $this->grantEntitlement($agencyA, MarketingBlockPackServiceProvider::FEATURE_CODE);

        $agencyB = $this->makeAgency(); // no entitlement

        $premiumBlocks = [$this->premiumBlock()];

        $tenantA = $this->makeTenant($agencyA);
        $templateA = $this->makeTemplate($agencyA, $premiumBlocks);
        $this->assignLayout($agencyA, $tenantA, $templateA);

        $tenantB = $this->makeTenant($agencyB);
        $templateB = $this->makeTemplate($agencyB, $premiumBlocks);
        $this->assignLayout($agencyB, $tenantB, $templateB);

        $payloadA = $this->renderer()->renderStorefront($tenantA, 'home');
        $payloadB = $this->renderer()->renderStorefront($tenantB, 'home');

        // Agency A: has entitlement → block rendered
        $this->assertContains('pricing_table', array_column($payloadA['blocks'], 'type'));

        // Agency B: no entitlement → block excluded
        $this->assertEmpty($payloadB['blocks']);
    }
}
