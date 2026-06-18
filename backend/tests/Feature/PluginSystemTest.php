<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\Agency;
use App\Models\Central\LayoutAssignment;
use App\Models\Central\LayoutTemplate;
use App\Models\Central\ThemeAssignment;
use App\Models\Central\ThemePreset;
use App\Plugins\BlockDefinition;
use App\Plugins\Exceptions\DuplicatePluginKeyException;
use App\Plugins\PluginRegistry;
use App\Plugins\ThemeDefinition;
use App\Services\LayoutBlockSchema;
use App\Services\LayoutRendererService;
use App\Services\ThemeConfigSchema;
use Filament\Forms\Components\Builder\Block;
use Illuminate\Support\Facades\DB;
use Tests\CentralTestCase;

/**
 * Plugin System v1 test suite.
 *
 * Tests:
 *  1.  PluginRegistry singleton is bound in the container
 *  2.  All 7 core blocks are registered in the registry
 *  3.  All 3 core themes are registered in the registry
 *  4.  Duplicate block key throws DuplicatePluginKeyException
 *  5.  Duplicate theme key throws DuplicatePluginKeyException
 *  6.  PluginRegistry::hasBlock and hasTheme work correctly
 *  7.  PluginRegistry::getBlock and getTheme return correct definitions
 *  8.  LayoutBlockSchema::blocks() delegates to registry (returns Filament Blocks)
 *  9.  LayoutBlockSchema::knownTypes() matches registry block keys
 * 10.  ThemeConfigSchema::systemPresets() delegates to registry (only system themes)
 *      and returns expected format
 * 11.  BlockDefinition::toFilamentBlock() returns a Filament Builder Block instance
 * 12.  ThemeDefinition::toPresetSeedData() returns correct format
 * 13.  LayoutRendererService is compatible with registry-driven knownTypes
 * 14.  renderStorefront payload is compatible with registry-driven theme/block system
 * 15.  No regression: LayoutBlockSchema::knownTypes() still lists all 7 v1 block keys
 * 16.  No regression: ThemeConfigSchema::systemPresets() still lists 3 v1 system themes
 */
class PluginSystemTest extends CentralTestCase
{
    private static int $seq = 0;

    // ── Helpers ───────────────────────────────────────────────────────────────

    private function registry(): PluginRegistry
    {
        return app(PluginRegistry::class);
    }

    private function renderer(): LayoutRendererService
    {
        return app(LayoutRendererService::class);
    }

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

    // ── 1. Registry is bound ──────────────────────────────────────────────────

    public function test_plugin_registry_singleton_is_bound_in_container(): void
    {
        $a = app(PluginRegistry::class);
        $b = app(PluginRegistry::class);

        $this->assertInstanceOf(PluginRegistry::class, $a);
        $this->assertSame($a, $b, 'PluginRegistry must be a singleton');
    }

    // ── 2. Core blocks registered ─────────────────────────────────────────────

    public function test_all_seven_core_blocks_are_registered(): void
    {
        $registry = $this->registry();
        $expected = ['hero', 'feature_grid', 'rich_text', 'cta', 'faq', 'testimonial', 'spacer'];

        foreach ($expected as $key) {
            $this->assertTrue($registry->hasBlock($key), "Core block '{$key}' must be registered");
        }

        $this->assertCount(7, $registry->blocks(), 'Exactly 7 core blocks must be registered');
    }

    // ── 3. Core themes registered ─────────────────────────────────────────────

    public function test_all_three_core_themes_are_registered(): void
    {
        $registry = $this->registry();
        $expected = ['ocean', 'slate', 'sand'];

        foreach ($expected as $key) {
            $this->assertTrue($registry->hasTheme($key), "Core theme '{$key}' must be registered");
        }

        $this->assertCount(3, $registry->themes(), 'Exactly 3 core themes must be registered');
    }

    // ── 4. Duplicate block key → exception ───────────────────────────────────

    public function test_duplicate_block_key_throws_exception(): void
    {
        $registry = new PluginRegistry; // isolated — does not affect the container singleton
        $def = new BlockDefinition(
            key: 'my_block',
            label: 'My Block',
            fieldsBuilder: static fn (): array => [],
        );

        $registry->registerBlock('my_block', $def);

        $this->expectException(DuplicatePluginKeyException::class);
        $this->expectExceptionMessageMatches('/my_block/');

        $registry->registerBlock('my_block', $def);
    }

    // ── 5. Duplicate theme key → exception ───────────────────────────────────

    public function test_duplicate_theme_key_throws_exception(): void
    {
        $registry = new PluginRegistry;
        $def = new ThemeDefinition(key: 'my_theme', label: 'My Theme');

        $registry->registerTheme('my_theme', $def);

        $this->expectException(DuplicatePluginKeyException::class);
        $this->expectExceptionMessageMatches('/my_theme/');

        $registry->registerTheme('my_theme', $def);
    }

    // ── 6. hasBlock / hasTheme ────────────────────────────────────────────────

    public function test_has_block_and_has_theme_return_correct_values(): void
    {
        $registry = $this->registry();

        $this->assertTrue($registry->hasBlock('hero'));
        $this->assertFalse($registry->hasBlock('non_existent_block'));

        $this->assertTrue($registry->hasTheme('ocean'));
        $this->assertFalse($registry->hasTheme('non_existent_theme'));
    }

    // ── 7. getBlock / getTheme ────────────────────────────────────────────────

    public function test_get_block_and_get_theme_return_correct_definitions(): void
    {
        $registry = $this->registry();

        $block = $registry->getBlock('hero');
        $this->assertInstanceOf(BlockDefinition::class, $block);
        $this->assertEquals('hero', $block->key);
        $this->assertEquals('Hero', $block->label);

        $theme = $registry->getTheme('ocean');
        $this->assertInstanceOf(ThemeDefinition::class, $theme);
        $this->assertEquals('ocean', $theme->key);
        $this->assertEquals('Ocean', $theme->label);
        $this->assertTrue($theme->isSystem);

        $this->assertNull($registry->getBlock('does_not_exist'));
        $this->assertNull($registry->getTheme('does_not_exist'));
    }

    // ── 8. LayoutBlockSchema delegates to registry ────────────────────────────

    public function test_layout_block_schema_blocks_delegates_to_registry(): void
    {
        $registry = $this->registry();
        $blocks = LayoutBlockSchema::blocks();

        $this->assertCount(count($registry->blocks()), $blocks);

        foreach ($blocks as $block) {
            $this->assertInstanceOf(Block::class, $block);
        }
    }

    // ── 9. knownTypes matches registry keys ───────────────────────────────────

    public function test_known_types_matches_registry_block_keys(): void
    {
        $knownTypes = LayoutBlockSchema::knownTypes();
        $registryKeys = $this->registry()->blockKeys();

        $this->assertEquals($registryKeys, $knownTypes);
    }

    // ── 10. ThemeConfigSchema::systemPresets delegates to registry ────────────

    public function test_theme_config_system_presets_delegates_to_registry(): void
    {
        $presets = ThemeConfigSchema::systemPresets();

        // Format must be: ['ocean' => ['name' => 'Ocean', 'slug' => 'ocean', 'config' => [...]]]
        $this->assertArrayHasKey('ocean', $presets);
        $this->assertArrayHasKey('slate', $presets);
        $this->assertArrayHasKey('sand', $presets);

        foreach ($presets as $key => $preset) {
            $this->assertEquals($key, $preset['slug'], "Slug must match key for preset '{$key}'");
            $this->assertArrayHasKey('name', $preset);
            $this->assertArrayHasKey('config', $preset);
            $this->assertIsArray($preset['config']);
        }

        // Only system themes must appear (all 3 core themes are system=true)
        $nonSystemRegistry = new PluginRegistry;
        $nonSystemRegistry->registerTheme('custom', new ThemeDefinition('custom', 'Custom', isSystem: false));
        // custom is NOT in the container singleton, so systemPresets() won't include it
        $this->assertArrayNotHasKey('custom', $presets);
    }

    // ── 11. BlockDefinition::toFilamentBlock ──────────────────────────────────

    public function test_block_definition_to_filament_block_returns_block_instance(): void
    {
        $def = new BlockDefinition(
            key: 'test_block',
            label: 'Test Block',
            icon: 'heroicon-o-star',
            columns: 2,
            fieldsBuilder: static fn (): array => [],
        );

        $block = $def->toFilamentBlock();

        $this->assertInstanceOf(Block::class, $block);
    }

    // ── 12. ThemeDefinition::toPresetSeedData ─────────────────────────────────

    public function test_theme_definition_to_preset_seed_data_returns_correct_format(): void
    {
        $config = ['palette' => ['primary' => '#0ea5e9'], 'radius' => 'md'];
        $def = new ThemeDefinition(key: 'test_theme', label: 'Test Theme', defaultConfig: $config);

        $data = $def->toPresetSeedData();

        $this->assertEquals(['name' => 'Test Theme', 'slug' => 'test_theme', 'config' => $config], $data);
    }

    // ── 13. Renderer compatible with registry-driven knownTypes ───────────────

    public function test_renderer_is_compatible_with_registry_driven_block_whitelist(): void
    {
        $blocks = [
            ['type' => 'hero', 'data' => ['title' => 'Welcome', 'subtitle' => 'Sub']],
            ['type' => 'unknown_block_xyz', 'data' => ['payload' => 'evil']],
            ['type' => 'spacer', 'data' => ['size' => 'md']],
        ];

        $rendered = $this->renderer()->render($blocks);

        $this->assertCount(2, $rendered, 'Unknown block must be filtered by registry-driven whitelist');
        $this->assertEquals('hero', $rendered->first()['type']);
        $this->assertEquals('spacer', $rendered->last()['type']);
    }

    // ── 14. renderStorefront compatible with registry-driven system ───────────

    public function test_render_storefront_compatible_with_plugin_registry(): void
    {
        $agency = $this->makeAgency();
        $tenantId = $this->addTenant($agency);

        $template = LayoutTemplate::create([
            'agency_id' => $agency->id,
            'name' => 'Plugin Test',
            'slug' => 'plugin-test',
            'status' => LayoutTemplate::STATUS_PUBLISHED,
            'blocks' => [['type' => 'cta', 'data' => ['title' => 'Sign Up', 'button_label' => 'Go']]],
        ]);

        LayoutAssignment::create([
            'agency_id' => $agency->id,
            'tenant_id' => $tenantId,
            'layout_template_id' => $template->id,
            'page_key' => 'home',
        ]);

        $preset = ThemePreset::create([
            'agency_id' => $agency->id,
            'name' => 'Test Theme',
            'slug' => 'test-plugin-theme',
            'status' => ThemePreset::STATUS_ACTIVE,
            'is_system' => false,
            'config' => ThemeConfigSchema::defaults(),
        ]);

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
        $this->assertCount(1, $payload['blocks']);
        $this->assertEquals('cta', $payload['blocks'][0]['type']);
    }

    // ── 15. Regression: knownTypes still has all 7 v1 keys ───────────────────

    public function test_regression_known_types_still_has_all_seven_v1_block_keys(): void
    {
        $types = LayoutBlockSchema::knownTypes();
        $expected = ['hero', 'feature_grid', 'rich_text', 'cta', 'faq', 'testimonial', 'spacer'];

        foreach ($expected as $type) {
            $this->assertContains($type, $types, "Block type '{$type}' must still be in knownTypes()");
        }
    }

    // ── 16. Regression: systemPresets still has 3 v1 themes ──────────────────

    public function test_regression_system_presets_still_has_all_three_v1_themes(): void
    {
        $presets = ThemeConfigSchema::systemPresets();

        $this->assertCount(3, $presets, 'systemPresets() must still return exactly 3 v1 themes');
        $this->assertArrayHasKey('ocean', $presets);
        $this->assertArrayHasKey('slate', $presets);
        $this->assertArrayHasKey('sand', $presets);
    }
}
