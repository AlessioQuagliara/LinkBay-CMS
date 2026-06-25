<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\PluginCatalogItem;
use App\Plugins\BlockDefinition;
use App\Plugins\MarketingBlockPack\MarketingBlockPackServiceProvider;
use App\Plugins\PluginRegistry;
use App\Plugins\PremiumThemePack\PremiumThemePackServiceProvider;
use App\Plugins\ThemeDefinition;
use Database\Seeders\PluginCatalogItemSeeder;
use Tests\CentralTestCase;

/**
 * PluginCatalogItemSeeder test suite.
 *
 * Tests:
 *  1.  Seeder creates a system item for each premium block featureCode
 *  2.  Seeder creates system items for theme_pack_editorial and theme_pack_business (Fase 4C)
 *  3.  Seeder is idempotent — running twice does not duplicate records
 *  4.  Seeder does not touch manually-created (is_system = false) items
 *  5.  System items are created with status = active
 *  6.  System items update name/type when re-seeded
 *  7.  Items without featureCode are not seeded (free blocks/themes)
 *  8.  Deduplication: same featureCode on block and theme creates one record
 */
class PluginCatalogItemSeederTest extends CentralTestCase
{
    private function runSeeder(): void
    {
        $this->seed(PluginCatalogItemSeeder::class);
    }

    // ── 1. Premium blocks are seeded ──────────────────────────────────────────

    public function test_seeder_creates_system_item_for_premium_block(): void
    {
        $this->runSeeder();

        $this->assertDatabaseHas('plugin_catalog_items', [
            'code' => MarketingBlockPackServiceProvider::FEATURE_CODE,
            'type' => PluginCatalogItem::TYPE_BLOCK_PACK,
            'status' => PluginCatalogItem::STATUS_ACTIVE,
            'is_system' => true,
        ], 'central');
    }

    // ── 2. Premium theme SKUs are seeded (Fase 4C: editorial + business) ──────

    public function test_seeder_creates_system_items_for_premium_theme_skus(): void
    {
        $this->runSeeder();

        foreach ([PremiumThemePackServiceProvider::FEATURE_CODE_EDITORIAL, PremiumThemePackServiceProvider::FEATURE_CODE_BUSINESS] as $code) {
            $this->assertDatabaseHas('plugin_catalog_items', [
                'code' => $code,
                'type' => PluginCatalogItem::TYPE_THEME_PACK,
                'status' => PluginCatalogItem::STATUS_ACTIVE,
                'is_system' => true,
            ], 'central');
        }
    }

    // ── 3. Idempotency ────────────────────────────────────────────────────────

    public function test_seeder_is_idempotent(): void
    {
        $this->runSeeder();
        $countAfterFirst = PluginCatalogItem::where('is_system', true)->count();

        $this->runSeeder();
        $countAfterSecond = PluginCatalogItem::where('is_system', true)->count();

        $this->assertEquals($countAfterFirst, $countAfterSecond, 'Running the seeder twice must not create duplicate records');
    }

    // ── 4. Manual items are not touched ──────────────────────────────────────

    public function test_seeder_does_not_modify_manually_created_items(): void
    {
        PluginCatalogItem::create([
            'code' => 'my_custom_feature',
            'type' => PluginCatalogItem::TYPE_FEATURE,
            'name' => 'Custom Feature',
            'status' => PluginCatalogItem::STATUS_DRAFT,
            'is_system' => false,
        ]);

        $this->runSeeder();

        $this->assertDatabaseHas('plugin_catalog_items', [
            'code' => 'my_custom_feature',
            'type' => PluginCatalogItem::TYPE_FEATURE,
            'status' => PluginCatalogItem::STATUS_DRAFT,
            'is_system' => false,
        ], 'central');
    }

    // ── 5. System items status = active ───────────────────────────────────────

    public function test_seeded_system_items_are_active(): void
    {
        $this->runSeeder();

        $nonActive = PluginCatalogItem::where('is_system', true)
            ->where('status', '!=', PluginCatalogItem::STATUS_ACTIVE)
            ->count();

        $this->assertEquals(0, $nonActive, 'All system items must be seeded with status = active');
    }

    // ── 6. Re-seed updates name/type if changed ───────────────────────────────

    public function test_seeder_updates_existing_system_item_on_reseed(): void
    {
        // Simulate a stale system item with wrong type
        PluginCatalogItem::create([
            'code' => MarketingBlockPackServiceProvider::FEATURE_CODE,
            'type' => PluginCatalogItem::TYPE_FEATURE, // wrong type
            'name' => 'Old Name',
            'status' => PluginCatalogItem::STATUS_DRAFT, // wrong status
            'is_system' => true,
        ]);

        $this->runSeeder();

        $item = PluginCatalogItem::where('code', MarketingBlockPackServiceProvider::FEATURE_CODE)
            ->where('is_system', true)
            ->first();

        $this->assertNotNull($item);
        $this->assertEquals(PluginCatalogItem::TYPE_BLOCK_PACK, $item->type);
        $this->assertEquals(PluginCatalogItem::STATUS_ACTIVE, $item->status);
    }

    // ── 7. Free blocks/themes are not seeded ─────────────────────────────────

    public function test_free_blocks_and_themes_are_not_seeded(): void
    {
        $registry = app(PluginRegistry::class);

        $freeBlockKeys = collect($registry->blocks())
            ->filter(fn ($def) => $def->featureCode === null)
            ->keys()
            ->all();

        $freeThemeKeys = collect($registry->themes())
            ->filter(fn ($def) => $def->featureCode === null)
            ->keys()
            ->all();

        $this->runSeeder();

        foreach ($freeBlockKeys as $key) {
            $this->assertDatabaseMissing('plugin_catalog_items', ['code' => $key], 'central');
        }

        foreach ($freeThemeKeys as $key) {
            $this->assertDatabaseMissing('plugin_catalog_items', ['code' => $key], 'central');
        }
    }

    // ── 8. Deduplication when same featureCode appears on block and theme ─────

    public function test_same_feature_code_on_block_and_theme_creates_one_record(): void
    {
        $sharedCode = 'shared_feature_code_test';

        $registry = app(PluginRegistry::class);

        // Register a block and a theme sharing the same featureCode
        $registry->registerBlock('test_dedup_block', new BlockDefinition(
            key: 'test_dedup_block',
            label: 'Dedup Test Block',
            fieldsBuilder: fn () => [],
            featureCode: $sharedCode,
        ));

        $registry->registerTheme('test_dedup_theme', new ThemeDefinition(
            key: 'test_dedup_theme',
            label: 'Dedup Test Theme',
            featureCode: $sharedCode,
        ));

        $this->runSeeder();

        $count = PluginCatalogItem::where('code', $sharedCode)->where('is_system', true)->count();
        $this->assertEquals(1, $count, 'Same featureCode on block and theme must produce one catalog item');
    }
}
