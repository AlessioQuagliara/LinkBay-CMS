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
use App\Models\Central\UsageEvent;
use App\Plugins\PluginRegistry;
use App\Plugins\PremiumThemePack\PremiumThemePackServiceProvider;
use App\Services\LayoutRendererService;
use App\Services\ThemeConfigSchema;
use App\Services\UsageEventService;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use Tests\CentralTestCase;

/**
 * Fase 5A — Usage Analytics Foundation test suite.
 *
 * Tests:
 *  1.  track() saves event with explicit agency_id
 *  2.  track() resolves agency_id from container binding
 *  3.  track() saves event with tenant_id
 *  4.  track() is fail-safe: DB exception → returns null, does not throw
 *  5.  track() logs a warning on failure
 *  6.  inferGroup() assigns 'storefront' group for storefront events
 *  7.  inferGroup() assigns 'panel' group for panel events
 *  8.  activeAgencies() counts only agencies active in the window
 *  9.  activeTenants() counts only tenants with storefront.rendered in the window
 * 10.  eventCount() scopes by event type and window
 * 11.  topTenants() orders tenants by event count descending
 * 12.  renderer tracks storefront.rendered without breaking output
 * 13.  renderer tracks theme.rendered when a premium theme is served
 * 14.  renderer tracks premium_block.rendered for premium blocks
 * 15.  renderer does NOT track theme.rendered when agency lacks entitlement
 * 16.  renderer does NOT break when tracking service is unavailable
 * 17.  no regression: existing agency preset output unchanged
 */
class UsageAnalyticsTest extends CentralTestCase
{
    private static int $seq = 0;

    // ── Helpers ───────────────────────────────────────────────────────────────

    private function makeAgency(?Plan $plan = null): Agency
    {
        self::$seq++;

        return Agency::create([
            'name' => 'Analytics Agency '.self::$seq,
            'slug' => 'analytics-agency-'.self::$seq,
            'brand_name' => 'Analytics Agency '.self::$seq,
            'status' => 'active',
            'billing_type' => 'monthly',
            'plan_id' => $plan?->id,
        ]);
    }

    private function makeTenant(Agency $agency): string
    {
        self::$seq++;
        $id = 'analytics-store-'.self::$seq;

        DB::connection('central')->table('tenants')->insert([
            'id' => $id,
            'name' => 'Analytics Store '.self::$seq,
            'status' => 'active',
            'agency_id' => $agency->id,
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        return $id;
    }

    private function makePublishedLayout(Agency $agency): LayoutTemplate
    {
        return LayoutTemplate::create([
            'agency_id' => $agency->id,
            'name' => 'Test Layout',
            'slug' => 'test-layout-'.self::$seq,
            'status' => LayoutTemplate::STATUS_PUBLISHED,
            'blocks' => [['type' => 'hero', 'data' => ['heading' => 'Hello', 'body' => '']]],
        ]);
    }

    private function assignLayout(Agency $agency, string $tenantId, LayoutTemplate $layout): void
    {
        LayoutAssignment::create([
            'agency_id' => $agency->id,
            'tenant_id' => $tenantId,
            'layout_template_id' => $layout->id,
            'page_key' => 'home',
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

    private function makeSystemPreset(string $slug): ThemePreset
    {
        $def = app(PluginRegistry::class)->getTheme($slug);

        return ThemePreset::create([
            'name' => ucfirst($slug),
            'slug' => $slug,
            'status' => ThemePreset::STATUS_ACTIVE,
            'is_system' => true,
            'config' => ThemeConfigSchema::normalize($def?->defaultConfig ?? []),
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

    private function svc(): UsageEventService
    {
        return app(UsageEventService::class);
    }

    // ── 1. track() with explicit agency_id ───────────────────────────────────

    public function test_track_saves_event_with_explicit_agency_id(): void
    {
        $agency = $this->makeAgency();

        $event = $this->svc()->track(
            eventType: UsageEvent::EVENT_THEME_PREVIEW_OPENED,
            agencyId: $agency->id,
            meta: ['theme_slug' => 'ocean'],
        );

        $this->assertNotNull($event);
        $this->assertSame(UsageEvent::EVENT_THEME_PREVIEW_OPENED, $event->event_type);
        $this->assertSame($agency->id, $event->agency_id);
        $this->assertSame(['theme_slug' => 'ocean'], $event->meta);

        $this->assertDatabaseHas('usage_events', [
            'id' => $event->id,
            'event_type' => UsageEvent::EVENT_THEME_PREVIEW_OPENED,
            'agency_id' => $agency->id,
        ], 'central');
    }

    // ── 2. track() resolves agency from container ─────────────────────────────

    public function test_track_resolves_agency_from_container_binding(): void
    {
        $agency = $this->makeAgency();
        app()->instance('current_agency', $agency);

        $event = $this->svc()->track(UsageEvent::EVENT_ENTITLEMENT_VIEWED);

        $this->assertNotNull($event);
        $this->assertSame($agency->id, $event->agency_id);

        app()->forgetInstance('current_agency');
    }

    // ── 3. track() with tenant_id ─────────────────────────────────────────────

    public function test_track_saves_tenant_id(): void
    {
        $agency = $this->makeAgency();
        $tenantId = $this->makeTenant($agency);

        $event = $this->svc()->track(
            eventType: UsageEvent::EVENT_STOREFRONT_RENDERED,
            tenantId: $tenantId,
            agencyId: $agency->id,
        );

        $this->assertSame($tenantId, $event?->tenant_id);
    }

    // ── 4. track() fail-safe on DB exception ──────────────────────────────────

    public function test_track_is_fail_safe_and_returns_null_on_exception(): void
    {
        // Drop the table inside the wrapping transaction — SQLite DDL is transactional,
        // so the table is restored after the test rolls back.
        DB::connection('central')->statement('DROP TABLE IF EXISTS usage_events');

        $result = (new UsageEventService)->track(UsageEvent::EVENT_THEME_PREVIEW_OPENED);

        $this->assertNull($result, 'track() must return null on failure, not throw');
    }

    // ── 5. track() logs warning on failure ────────────────────────────────────

    public function test_track_logs_warning_on_failure(): void
    {
        Log::shouldReceive('warning')
            ->once()
            ->withArgs(fn (string $message, array $context = []) => str_starts_with($message, 'UsageEventService'));

        DB::connection('central')->statement('DROP TABLE IF EXISTS usage_events');

        (new UsageEventService)->track(UsageEvent::EVENT_THEME_PREVIEW_OPENED);
    }

    // ── 6. inferGroup for storefront events ───────────────────────────────────

    public function test_storefront_events_get_storefront_group(): void
    {
        $event = $this->svc()->track(UsageEvent::EVENT_STOREFRONT_RENDERED);

        $this->assertSame(UsageEvent::GROUP_STOREFRONT, $event?->event_group);
    }

    // ── 7. inferGroup for panel events ────────────────────────────────────────

    public function test_panel_events_get_panel_group(): void
    {
        $event = $this->svc()->track(UsageEvent::EVENT_THEME_FORK_CREATED);

        $this->assertSame(UsageEvent::GROUP_PANEL, $event?->event_group);
    }

    // ── 8. activeAgencies() window ────────────────────────────────────────────

    public function test_active_agencies_counts_only_agencies_in_window(): void
    {
        $agencyA = $this->makeAgency();
        $agencyB = $this->makeAgency();
        $agencyC = $this->makeAgency();

        // A and B have recent events
        $this->svc()->track(UsageEvent::EVENT_STOREFRONT_RENDERED, agencyId: $agencyA->id);
        $this->svc()->track(UsageEvent::EVENT_STOREFRONT_RENDERED, agencyId: $agencyB->id);

        // C has only an old event (outside 7-day window)
        UsageEvent::create([
            'agency_id' => $agencyC->id,
            'event_type' => UsageEvent::EVENT_STOREFRONT_RENDERED,
            'event_group' => UsageEvent::GROUP_STOREFRONT,
            'occurred_at' => now()->subDays(10),
        ]);

        $count = $this->svc()->activeAgencies(7);

        $this->assertSame(2, $count);
    }

    // ── 9. activeTenants() counts only storefront.rendered ────────────────────

    public function test_active_tenants_counts_only_storefront_rendered(): void
    {
        $agency = $this->makeAgency();
        $storeA = $this->makeTenant($agency);
        $storeB = $this->makeTenant($agency);
        $storeC = $this->makeTenant($agency);

        $this->svc()->track(UsageEvent::EVENT_STOREFRONT_RENDERED, tenantId: $storeA, agencyId: $agency->id);
        $this->svc()->track(UsageEvent::EVENT_STOREFRONT_RENDERED, tenantId: $storeB, agencyId: $agency->id);
        // C only has a non-storefront event
        $this->svc()->track(UsageEvent::EVENT_THEME_PREVIEW_OPENED, tenantId: $storeC, agencyId: $agency->id);

        $count = $this->svc()->activeTenants(30);

        $this->assertSame(2, $count);
    }

    // ── 10. eventCount() scopes correctly ─────────────────────────────────────

    public function test_event_count_scopes_by_type_and_window(): void
    {
        $agency = $this->makeAgency();

        $this->svc()->track(UsageEvent::EVENT_THEME_FORK_CREATED, agencyId: $agency->id);
        $this->svc()->track(UsageEvent::EVENT_THEME_FORK_CREATED, agencyId: $agency->id);
        $this->svc()->track(UsageEvent::EVENT_THEME_PREVIEW_OPENED, agencyId: $agency->id);

        // Old fork event outside 7-day window
        UsageEvent::create([
            'agency_id' => $agency->id,
            'event_type' => UsageEvent::EVENT_THEME_FORK_CREATED,
            'event_group' => UsageEvent::GROUP_PANEL,
            'occurred_at' => now()->subDays(10),
        ]);

        $this->assertSame(2, $this->svc()->eventCount(UsageEvent::EVENT_THEME_FORK_CREATED, 7));
        $this->assertSame(1, $this->svc()->eventCount(UsageEvent::EVENT_THEME_PREVIEW_OPENED, 7));
    }

    // ── 11. topTenants() orders by event count ─────────────────────────────────

    public function test_top_tenants_returns_tenants_ordered_by_event_count(): void
    {
        $agency = $this->makeAgency();
        $storeA = $this->makeTenant($agency);
        $storeB = $this->makeTenant($agency);

        // storeB has more events
        foreach (range(1, 3) as $i) {
            $this->svc()->track(UsageEvent::EVENT_STOREFRONT_RENDERED, tenantId: $storeB, agencyId: $agency->id);
        }
        $this->svc()->track(UsageEvent::EVENT_STOREFRONT_RENDERED, tenantId: $storeA, agencyId: $agency->id);

        $top = $this->svc()->topTenants(5, 30);

        $this->assertSame($storeB, $top->first()->tenant_id);
        $this->assertSame(3, (int) $top->first()->event_count);
    }

    // ── 12. renderer tracks storefront.rendered ──────────────────────────────

    public function test_renderer_tracks_storefront_rendered_without_breaking_output(): void
    {
        $agency = $this->makeAgency();
        $tenantId = $this->makeTenant($agency);
        $layout = $this->makePublishedLayout($agency);
        $this->assignLayout($agency, $tenantId, $layout);

        $result = app(LayoutRendererService::class)->renderStorefront($tenantId, 'home');

        $this->assertNotNull($result, 'Renderer must return a valid payload');
        $this->assertArrayHasKey('theme', $result);
        $this->assertArrayHasKey('blocks', $result);

        $this->assertDatabaseHas('usage_events', [
            'event_type' => UsageEvent::EVENT_STOREFRONT_RENDERED,
            'tenant_id' => $tenantId,
            'agency_id' => $agency->id,
        ], 'central');
    }

    // ── 13. renderer tracks theme.rendered for premium themes ────────────────

    public function test_renderer_tracks_theme_rendered_for_premium_themes(): void
    {
        $agency = $this->makeAgency();
        $tenantId = $this->makeTenant($agency);
        $this->grantEntitlement($agency, PremiumThemePackServiceProvider::FEATURE_CODE_EDITORIAL);

        $layout = $this->makePublishedLayout($agency);
        $this->assignLayout($agency, $tenantId, $layout);

        $midnightPreset = $this->makeSystemPreset('midnight');
        $this->assignTheme($agency, $tenantId, $midnightPreset);

        app(LayoutRendererService::class)->renderStorefront($tenantId, 'home');

        $this->assertDatabaseHas('usage_events', [
            'event_type' => UsageEvent::EVENT_THEME_RENDERED,
            'tenant_id' => $tenantId,
            'agency_id' => $agency->id,
        ], 'central');
    }

    // ── 14. renderer tracks premium_block.rendered ────────────────────────────

    public function test_renderer_tracks_premium_block_rendered(): void
    {
        $agency = $this->makeAgency();
        $tenantId = $this->makeTenant($agency);

        $premiumItem = PluginCatalogItem::firstOrCreate(
            ['code' => 'block_pack_marketing'],
            ['type' => PluginCatalogItem::TYPE_BLOCK_PACK, 'name' => 'Marketing Block Pack', 'status' => PluginCatalogItem::STATUS_ACTIVE],
        );
        AgencyEntitlement::create([
            'agency_id' => $agency->id,
            'catalog_item_id' => $premiumItem->id,
            'source' => AgencyEntitlement::SOURCE_MANUAL,
            'status' => AgencyEntitlement::STATUS_ACTIVE,
        ]);

        $layout = LayoutTemplate::create([
            'agency_id' => $agency->id,
            'name' => 'Premium Block Layout',
            'slug' => 'premium-block-layout-'.self::$seq,
            'status' => LayoutTemplate::STATUS_PUBLISHED,
            'blocks' => [
                ['type' => 'pricing_table', 'data' => ['section_title' => 'Prezzi', 'tiers' => [['name' => 'Base', 'price' => '€9', 'period' => '/mese', 'features' => []]]]],
            ],
        ]);
        $this->assignLayout($agency, $tenantId, $layout);

        app(LayoutRendererService::class)->renderStorefront($tenantId, 'home');

        $this->assertDatabaseHas('usage_events', [
            'event_type' => UsageEvent::EVENT_PREMIUM_BLOCK_RENDERED,
            'tenant_id' => $tenantId,
        ], 'central');
    }

    // ── 15. renderer does NOT track theme.rendered without entitlement ─────────

    public function test_renderer_does_not_track_premium_theme_when_agency_lacks_entitlement(): void
    {
        $agency = $this->makeAgency();
        $tenantId = $this->makeTenant($agency);

        $layout = $this->makePublishedLayout($agency);
        $this->assignLayout($agency, $tenantId, $layout);

        $midnightPreset = $this->makeSystemPreset('midnight');
        $this->assignTheme($agency, $tenantId, $midnightPreset);

        // Agency has NO editorial entitlement — should fall back to defaults
        app(LayoutRendererService::class)->renderStorefront($tenantId, 'home');

        $themeRenderedEvents = UsageEvent::where('event_type', UsageEvent::EVENT_THEME_RENDERED)
            ->where('tenant_id', $tenantId)
            ->count();

        $this->assertSame(0, $themeRenderedEvents, 'theme.rendered must not be tracked when access is denied');
    }

    // ── 16. renderer output is not broken when tracking service fails ─────────

    public function test_renderer_output_is_not_broken_when_tracking_throws(): void
    {
        $agency = $this->makeAgency();
        $tenantId = $this->makeTenant($agency);
        $layout = $this->makePublishedLayout($agency);
        $this->assignLayout($agency, $tenantId, $layout);

        // Trigger tracking failures by dropping the table — the renderer must still produce output
        DB::connection('central')->statement('DROP TABLE IF EXISTS usage_events');

        $output = app(LayoutRendererService::class)->renderStorefront($tenantId, 'home');

        $this->assertNotNull($output, 'Renderer must return a valid payload even when tracking fails');
        $this->assertArrayHasKey('blocks', $output);
    }

    // ── 17. no regression: existing agency preset output unchanged ─────────────

    public function test_existing_agency_preset_output_is_unchanged(): void
    {
        $agency = $this->makeAgency();
        $tenantId = $this->makeTenant($agency);
        $layout = $this->makePublishedLayout($agency);
        $this->assignLayout($agency, $tenantId, $layout);

        $agencyPreset = ThemePreset::create([
            'agency_id' => $agency->id,
            'name' => 'Custom',
            'slug' => 'custom-regression-'.self::$seq,
            'status' => ThemePreset::STATUS_ACTIVE,
            'is_system' => false,
            'config' => ThemeConfigSchema::defaults(),
        ]);
        $this->assignTheme($agency, $tenantId, $agencyPreset);

        $result = app(LayoutRendererService::class)->renderStorefront($tenantId, 'home');

        $this->assertNotNull($result);
        $this->assertEquals(ThemeConfigSchema::normalize(ThemeConfigSchema::defaults()), $result['theme']);
        $this->assertCount(1, $result['blocks']);
        $this->assertSame('hero', $result['blocks'][0]['type']);
    }

    // ── Teardown ──────────────────────────────────────────────────────────────

    protected function tearDown(): void
    {
        app()->forgetInstance('current_agency');
        parent::tearDown();
    }
}
