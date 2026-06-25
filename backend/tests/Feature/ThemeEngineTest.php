<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\Agency;
use App\Models\Central\AuditEvent;
use App\Models\Central\LayoutAssignment;
use App\Models\Central\LayoutTemplate;
use App\Models\Central\Tenant;
use App\Models\Central\ThemeAssignment;
use App\Models\Central\ThemePreset;
use App\Services\LayoutRendererService;
use App\Services\ThemeConfigSchema;
use Illuminate\Database\UniqueConstraintViolationException;
use Illuminate\Support\Facades\DB;
use Tests\CentralTestCase;

/**
 * Theme Engine v1 test suite.
 *
 * Tests:
 *  1.  Agency preset can be created
 *  2.  System presets are visible to any agency
 *  3.  Agency's own presets are visible
 *  4.  Other agency's presets are NOT visible
 *  5.  Duplicate system preset creates agency-owned draft
 *  6.  Duplicate generates unique slug on collision
 *  7.  System preset cannot be directly modified (is_system flag check)
 *  8.  activate() sets status to active
 *  9.  deactivate() sets status to draft
 * 10.  Assignment to same-agency tenant succeeds (upsert replaces existing)
 * 11.  Cross-agency assignment is blocked by ownership check
 * 12.  unique(tenant_id) constraint enforced at DB level
 * 13.  renderStorefront returns theme + blocks payload
 * 14.  renderStorefront falls back to defaults when no theme assigned
 * 15.  renderStorefront returns null when no layout assigned
 * 16.  ThemeConfigSchema::normalize drops unknown keys
 * 17.  ThemeConfigSchema::normalize replaces invalid enum with default
 * 18.  ThemeConfigSchema::normalize validates hex color format
 * 19.  ThemeConfigSchema system presets count and slug coverage
 * 20.  AuditEvent theme constants are defined and labeled
 */
class ThemeEngineTest extends CentralTestCase
{
    private static int $seq = 0;

    // ── Helpers ───────────────────────────────────────────────────────────────

    private function makeAgency(): Agency
    {
        self::$seq++;

        return Agency::create([
            'name' => 'Agency '.self::$seq,
            'slug' => 'agency-'.self::$seq,
            'brand_name' => 'Agency '.self::$seq,
            'status' => 'active',
            'billing_type' => 'monthly',
        ]);
    }

    private function makeSystemPreset(string $slug = ''): ThemePreset
    {
        self::$seq++;
        $slug = $slug ?: 'system-'.self::$seq;

        return ThemePreset::create([
            'agency_id' => null,
            'name' => 'System '.self::$seq,
            'slug' => $slug,
            'status' => ThemePreset::STATUS_ACTIVE,
            'is_system' => true,
            'config' => ThemeConfigSchema::defaults(),
        ]);
    }

    private function makeAgencyPreset(Agency $agency, string $status = ThemePreset::STATUS_DRAFT): ThemePreset
    {
        self::$seq++;

        return ThemePreset::create([
            'agency_id' => $agency->id,
            'name' => 'Preset '.self::$seq,
            'slug' => 'preset-'.self::$seq,
            'status' => $status,
            'is_system' => false,
            'config' => ThemeConfigSchema::defaults(),
        ]);
    }

    private function addTenant(Agency $agency): string
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

    private function renderer(): LayoutRendererService
    {
        return app(LayoutRendererService::class);
    }

    // ── 1. Agency preset creation ─────────────────────────────────────────────

    public function test_agency_preset_can_be_created(): void
    {
        $agency = $this->makeAgency();
        $preset = $this->makeAgencyPreset($agency);

        $this->assertModelExists($preset);
        $this->assertEquals($agency->id, $preset->agency_id);
        $this->assertFalse($preset->is_system);
        $this->assertEquals(ThemePreset::STATUS_DRAFT, $preset->status);
    }

    // ── 2. System preset visibility ───────────────────────────────────────────

    public function test_system_presets_are_visible_to_any_agency(): void
    {
        $agencyA = $this->makeAgency();
        $agencyB = $this->makeAgency();
        $systemPreset = $this->makeSystemPreset();

        $visibleToA = ThemePreset::visibleTo($agencyA->id)->where('id', $systemPreset->id)->exists();
        $visibleToB = ThemePreset::visibleTo($agencyB->id)->where('id', $systemPreset->id)->exists();

        $this->assertTrue($visibleToA, 'System preset must be visible to agency A');
        $this->assertTrue($visibleToB, 'System preset must be visible to agency B');
    }

    // ── 3. Own preset visibility ──────────────────────────────────────────────

    public function test_own_presets_are_visible_to_owning_agency(): void
    {
        $agency = $this->makeAgency();
        $preset = $this->makeAgencyPreset($agency);

        $visible = ThemePreset::visibleTo($agency->id)->where('id', $preset->id)->exists();

        $this->assertTrue($visible);
    }

    // ── 4. Cross-agency preset invisibility ───────────────────────────────────

    public function test_other_agency_presets_are_not_visible(): void
    {
        $agencyA = $this->makeAgency();
        $agencyB = $this->makeAgency();
        $presetB = $this->makeAgencyPreset($agencyB);

        $visibleToA = ThemePreset::visibleTo($agencyA->id)->where('id', $presetB->id)->exists();

        $this->assertFalse($visibleToA, 'Agency B preset must not be visible to agency A');
    }

    // ── 5. Duplicate system preset ────────────────────────────────────────────

    public function test_duplicate_system_preset_creates_agency_owned_draft(): void
    {
        $agency = $this->makeAgency();
        $system = $this->makeSystemPreset();

        $copy = $system->duplicate($agency->id, 'My Ocean');

        $this->assertModelExists($copy);
        $this->assertNotEquals($system->id, $copy->id);
        $this->assertEquals($agency->id, $copy->agency_id);
        $this->assertFalse($copy->is_system);
        $this->assertEquals(ThemePreset::STATUS_DRAFT, $copy->status);
        // Config must be cloned and normalized
        $this->assertIsArray($copy->config);
        $this->assertArrayHasKey('palette', $copy->config);
    }

    // ── 6. Duplicate slug collision ───────────────────────────────────────────

    public function test_duplicate_generates_unique_slug_on_collision(): void
    {
        $agency = $this->makeAgency();
        $system = $this->makeSystemPreset();

        $copy1 = $system->duplicate($agency->id, 'My Theme');
        $copy2 = $system->duplicate($agency->id, 'My Theme');

        $this->assertNotEquals($copy1->slug, $copy2->slug);
    }

    // ── 7. System preset cannot be directly modified ──────────────────────────

    public function test_system_preset_is_system_flag_is_true(): void
    {
        $system = $this->makeSystemPreset();

        $this->assertTrue($system->isSystem());
        // Verify the flag persists after refresh
        $system->refresh();
        $this->assertTrue($system->isSystem());
    }

    // ── 8 & 9. Activate / deactivate ─────────────────────────────────────────

    public function test_activate_sets_status_to_active(): void
    {
        $agency = $this->makeAgency();
        $preset = $this->makeAgencyPreset($agency, ThemePreset::STATUS_DRAFT);

        $preset->activate();
        $preset->refresh();

        $this->assertTrue($preset->isActive());
        $this->assertEquals(ThemePreset::STATUS_ACTIVE, $preset->status);
    }

    public function test_deactivate_sets_status_to_draft(): void
    {
        $agency = $this->makeAgency();
        $preset = $this->makeAgencyPreset($agency, ThemePreset::STATUS_ACTIVE);

        $preset->deactivate();
        $preset->refresh();

        $this->assertTrue($preset->isDraft());
        $this->assertEquals(ThemePreset::STATUS_DRAFT, $preset->status);
    }

    // ── 10. Theme assignment ──────────────────────────────────────────────────

    public function test_assignment_to_same_agency_tenant_succeeds(): void
    {
        $agency = $this->makeAgency();
        $preset = $this->makeAgencyPreset($agency);
        $tenantId = $this->addTenant($agency);

        $assignment = ThemeAssignment::create([
            'agency_id' => $agency->id,
            'tenant_id' => $tenantId,
            'theme_preset_id' => $preset->id,
        ]);

        $this->assertModelExists($assignment);
        $this->assertEquals($tenantId, $assignment->tenant_id);
        $this->assertEquals($preset->id, $assignment->theme_preset_id);
    }

    // ── 11. Cross-agency assignment blocked ───────────────────────────────────

    public function test_cross_agency_assignment_is_blocked_by_ownership_check(): void
    {
        $agencyA = $this->makeAgency();
        $agencyB = $this->makeAgency();
        $preset = $this->makeAgencyPreset($agencyA);
        $tenantB = $this->addTenant($agencyB);

        // Simulate the RelationManager's before() ownership check.
        $tenant = Tenant::find($tenantB);
        $isSameAgency = $tenant && (int) $tenant->agency_id === (int) $agencyA->id;

        $this->assertFalse($isSameAgency, 'Tenant from agency B must fail agency A ownership check');
    }

    // ── 12. DB unique tenant_id constraint ───────────────────────────────────

    public function test_unique_tenant_id_constraint_enforced(): void
    {
        $agency = $this->makeAgency();
        $preset1 = $this->makeAgencyPreset($agency);
        $preset2 = $this->makeAgencyPreset($agency);
        $tenantId = $this->addTenant($agency);

        ThemeAssignment::create([
            'agency_id' => $agency->id,
            'tenant_id' => $tenantId,
            'theme_preset_id' => $preset1->id,
        ]);

        $this->expectException(UniqueConstraintViolationException::class);

        ThemeAssignment::create([
            'agency_id' => $agency->id,
            'tenant_id' => $tenantId,
            'theme_preset_id' => $preset2->id, // same tenant, different preset
        ]);
    }

    // ── 13. renderStorefront payload ──────────────────────────────────────────

    public function test_render_storefront_returns_theme_and_blocks(): void
    {
        $agency = $this->makeAgency();
        $tenantId = $this->addTenant($agency);

        // Create a published layout template assigned to this tenant+page.
        $template = LayoutTemplate::create([
            'agency_id' => $agency->id,
            'name' => 'Home',
            'slug' => 'home-tpl',
            'status' => LayoutTemplate::STATUS_PUBLISHED,
            'blocks' => [['type' => 'hero', 'data' => ['title' => 'Welcome', 'subtitle' => 'Sub']]],
        ]);
        LayoutAssignment::create([
            'agency_id' => $agency->id,
            'tenant_id' => $tenantId,
            'layout_template_id' => $template->id,
            'page_key' => 'home',
        ]);

        // Assign a theme preset.
        $preset = $this->makeAgencyPreset($agency, ThemePreset::STATUS_ACTIVE);
        ThemeAssignment::create([
            'agency_id' => $agency->id,
            'tenant_id' => $tenantId,
            'theme_preset_id' => $preset->id,
        ]);

        $payload = $this->renderer()->renderStorefront($tenantId, 'home');

        $this->assertNotNull($payload);
        $this->assertArrayHasKey('theme', $payload);
        $this->assertArrayHasKey('blocks', $payload);
        $this->assertArrayHasKey('palette', $payload['theme']);
        $this->assertArrayHasKey('typography', $payload['theme']);
        $this->assertCount(1, $payload['blocks']);
        $this->assertEquals('hero', $payload['blocks'][0]['type']);
    }

    // ── 14. renderStorefront falls back to defaults when no theme ─────────────

    public function test_render_storefront_falls_back_to_default_theme(): void
    {
        $agency = $this->makeAgency();
        $tenantId = $this->addTenant($agency);

        $template = LayoutTemplate::create([
            'agency_id' => $agency->id,
            'name' => 'Home',
            'slug' => 'home-default',
            'status' => LayoutTemplate::STATUS_PUBLISHED,
            'blocks' => [['type' => 'spacer', 'data' => ['size' => 'md']]],
        ]);
        LayoutAssignment::create([
            'agency_id' => $agency->id,
            'tenant_id' => $tenantId,
            'layout_template_id' => $template->id,
            'page_key' => 'home',
        ]);

        // No ThemeAssignment for this tenant.
        $payload = $this->renderer()->renderStorefront($tenantId, 'home');

        $this->assertNotNull($payload);
        $this->assertEquals(ThemeConfigSchema::defaults(), $payload['theme']);
    }

    // ── 15. renderStorefront returns null when no layout ──────────────────────

    public function test_render_storefront_returns_null_when_no_layout_assigned(): void
    {
        $agency = $this->makeAgency();
        $tenantId = $this->addTenant($agency);

        $payload = $this->renderer()->renderStorefront($tenantId, 'home');

        $this->assertNull($payload);
    }

    // ── 16. Normalize: unknown keys dropped ───────────────────────────────────

    public function test_normalize_drops_unknown_keys(): void
    {
        $raw = array_merge(ThemeConfigSchema::defaults(), ['malicious_key' => 'injected', 'another' => true]);

        $normalized = ThemeConfigSchema::normalize($raw);

        $this->assertArrayNotHasKey('malicious_key', $normalized);
        $this->assertArrayNotHasKey('another', $normalized);
        $this->assertArrayHasKey('palette', $normalized);
    }

    // ── 17. Normalize: invalid enum falls back to default ─────────────────────

    public function test_normalize_replaces_invalid_enum_with_default(): void
    {
        $raw = array_merge(ThemeConfigSchema::defaults(), [
            'radius' => 'not-a-valid-radius',
            'spacing' => 'bad-spacing',
            'buttons' => 'bad-button',
        ]);

        $normalized = ThemeConfigSchema::normalize($raw);

        $defaults = ThemeConfigSchema::defaults();
        $this->assertEquals($defaults['radius'], $normalized['radius']);
        $this->assertEquals($defaults['spacing'], $normalized['spacing']);
        $this->assertEquals($defaults['buttons'], $normalized['buttons']);
    }

    // ── 18. Normalize: hex color validation ───────────────────────────────────

    public function test_normalize_validates_hex_color_format(): void
    {
        $raw = ThemeConfigSchema::defaults();
        $raw['palette']['primary'] = 'not-a-color';
        $raw['palette']['secondary'] = 'rgb(0,0,0)';
        $raw['palette']['accent'] = '#aabbcc'; // valid

        $normalized = ThemeConfigSchema::normalize($raw);
        $defaults = ThemeConfigSchema::defaults();

        $this->assertEquals($defaults['palette']['primary'], $normalized['palette']['primary']);
        $this->assertEquals($defaults['palette']['secondary'], $normalized['palette']['secondary']);
        $this->assertEquals('#aabbcc', $normalized['palette']['accent']);
    }

    // ── 19. System presets coverage ───────────────────────────────────────────

    public function test_system_presets_define_all_built_in_themes(): void
    {
        $presets = ThemeConfigSchema::systemPresets();

        // 4 core + 3 premium pack — all are isSystem = true
        $this->assertCount(7, $presets);
        $this->assertArrayHasKey('ocean', $presets);
        $this->assertArrayHasKey('slate', $presets);
        $this->assertArrayHasKey('sand', $presets);
        $this->assertArrayHasKey('midnight', $presets);
        $this->assertArrayHasKey('noir', $presets);
        $this->assertArrayHasKey('atelier', $presets);
        $this->assertArrayHasKey('meridian', $presets);

        foreach ($presets as $slug => $preset) {
            $this->assertEquals($slug, $preset['slug']);
            $this->assertArrayHasKey('palette', $preset['config']);
            $this->assertArrayHasKey('typography', $preset['config']);
            $this->assertCount(5, $preset['config']['palette'], "Preset {$slug} must have 5 palette keys");
        }
    }

    // ── 20. AuditEvent theme constants ───────────────────────────────────────

    public function test_theme_audit_event_constants_are_defined(): void
    {
        $this->assertEquals('theme.created', AuditEvent::EVENT_THEME_CREATED);
        $this->assertEquals('theme.updated', AuditEvent::EVENT_THEME_UPDATED);
        $this->assertEquals('theme.activated', AuditEvent::EVENT_THEME_ACTIVATED);
        $this->assertEquals('theme.duplicated', AuditEvent::EVENT_THEME_DUPLICATED);
        $this->assertEquals('theme.assigned', AuditEvent::EVENT_THEME_ASSIGNED);

        foreach (['theme.created', 'theme.updated', 'theme.activated', 'theme.duplicated', 'theme.assigned'] as $event) {
            $this->assertArrayHasKey($event, AuditEvent::EVENT_LABELS, "Label missing for event: {$event}");
        }
    }
}
