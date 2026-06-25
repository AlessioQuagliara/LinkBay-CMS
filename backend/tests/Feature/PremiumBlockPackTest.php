<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\Agency;
use App\Models\Central\AgencyEntitlement;
use App\Models\Central\Plan;
use App\Models\Central\PluginCatalogItem;
use App\Plugins\MarketingBlockPack\MarketingBlockPackServiceProvider;
use App\Plugins\PluginRegistry;
use App\Services\LayoutBlockSchema;
use Tests\CentralTestCase;

/**
 * Premium Block Pack v1 test suite.
 *
 * Tests:
 *  1.  All 5 premium blocks are registered in the registry
 *  2.  Premium blocks carry featureCode = block_pack_marketing
 *  3.  Free blocks do not carry a featureCode (regression)
 *  4.  blocksForAgency() returns only free blocks with no entitlement
 *  5.  blocksForAgency() returns free + premium blocks with active entitlement
 *  6.  blocksForAgency() returns free + premium blocks via plan feature
 *  7.  blocksForAgency(null) returns only free blocks
 *  8.  premiumViolation() returns null when blocks array has no premium blocks
 *  9.  premiumViolation() returns null when agency has entitlement + uses premium block
 * 10.  premiumViolation() returns error message when no entitlement + premium block present
 * 11.  premiumViolation() returns null when premium block is absent from data (no violation)
 * 12.  knownTypes() includes premium block keys (renderer whitelist unchanged)
 * 13.  blocksForAgency() filters out blocks from revoked entitlement
 * 14.  PluginRegistry has 12 blocks total (7 free + 5 premium)
 */
class PremiumBlockPackTest extends CentralTestCase
{
    private static int $seq = 0;

    private const PREMIUM_BLOCKS = [
        'pricing_table',
        'logo_cloud',
        'stats_strip',
        'testimonial_carousel',
        'cta_split',
    ];

    private const FREE_BLOCKS = [
        'hero',
        'feature_grid',
        'rich_text',
        'cta',
        'faq',
        'testimonial',
        'spacer',
    ];

    // ── Helpers ───────────────────────────────────────────────────────────────

    private function registry(): PluginRegistry
    {
        return app(PluginRegistry::class);
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

    private function grantPackEntitlement(Agency $agency): AgencyEntitlement
    {
        $item = PluginCatalogItem::firstOrCreate(
            ['code' => MarketingBlockPackServiceProvider::FEATURE_CODE],
            [
                'type' => PluginCatalogItem::TYPE_BLOCK_PACK,
                'name' => 'Marketing Block Pack',
                'status' => PluginCatalogItem::STATUS_ACTIVE,
            ]
        );

        return AgencyEntitlement::create([
            'agency_id' => $agency->id,
            'catalog_item_id' => $item->id,
            'source' => AgencyEntitlement::SOURCE_MANUAL,
            'status' => AgencyEntitlement::STATUS_ACTIVE,
        ]);
    }

    // ── 1. All 5 premium blocks registered ───────────────────────────────────

    public function test_all_five_premium_blocks_are_registered(): void
    {
        $registry = $this->registry();

        foreach (self::PREMIUM_BLOCKS as $key) {
            $this->assertTrue($registry->hasBlock($key), "Premium block '{$key}' must be registered");
        }
    }

    // ── 2. Premium blocks carry featureCode ───────────────────────────────────

    public function test_premium_blocks_carry_correct_feature_code(): void
    {
        $registry = $this->registry();

        foreach (self::PREMIUM_BLOCKS as $key) {
            $def = $registry->getBlock($key);
            $this->assertEquals(
                MarketingBlockPackServiceProvider::FEATURE_CODE,
                $def->featureCode,
                "Block '{$key}' must have featureCode = block_pack_marketing"
            );
        }
    }

    // ── 3. Free blocks have no featureCode (regression) ──────────────────────

    public function test_free_blocks_have_no_feature_code(): void
    {
        $registry = $this->registry();

        foreach (self::FREE_BLOCKS as $key) {
            $def = $registry->getBlock($key);
            $this->assertNull($def->featureCode, "Free block '{$key}' must not have a featureCode");
        }
    }

    // ── 4. blocksForAgency() returns only free blocks with no entitlement ─────

    public function test_blocks_for_agency_returns_only_free_blocks_without_entitlement(): void
    {
        $agency = $this->makeAgency();
        $blocks = LayoutBlockSchema::blocksForAgency($agency);
        $keys = array_map(fn ($b) => $b->getName(), $blocks);

        foreach (self::FREE_BLOCKS as $key) {
            $this->assertContains($key, $keys, "Free block '{$key}' must be visible without entitlement");
        }

        foreach (self::PREMIUM_BLOCKS as $key) {
            $this->assertNotContains($key, $keys, "Premium block '{$key}' must NOT be visible without entitlement");
        }
    }

    // ── 5. blocksForAgency() returns all blocks with active entitlement ───────

    public function test_blocks_for_agency_returns_all_blocks_with_active_entitlement(): void
    {
        $agency = $this->makeAgency();
        $this->grantPackEntitlement($agency);

        $blocks = LayoutBlockSchema::blocksForAgency($agency);
        $keys = array_map(fn ($b) => $b->getName(), $blocks);

        foreach (self::FREE_BLOCKS as $key) {
            $this->assertContains($key, $keys, "Free block '{$key}' must be visible with entitlement");
        }

        foreach (self::PREMIUM_BLOCKS as $key) {
            $this->assertContains($key, $keys, "Premium block '{$key}' must be visible with entitlement");
        }
    }

    // ── 6. blocksForAgency() returns all blocks via plan feature ──────────────

    public function test_blocks_for_agency_returns_all_blocks_via_plan(): void
    {
        self::$seq++;
        $plan = Plan::create([
            'name' => 'Pro Plan '.self::$seq,
            'slug' => 'pro-plan-'.self::$seq,
            'price' => 199,
            'billing_interval' => 'month',
            'features' => [],
            'limits' => [MarketingBlockPackServiceProvider::FEATURE_CODE => true],
            'is_active' => true,
        ]);
        $agency = $this->makeAgency($plan);

        $blocks = LayoutBlockSchema::blocksForAgency($agency);
        $keys = array_map(fn ($b) => $b->getName(), $blocks);

        foreach (self::PREMIUM_BLOCKS as $key) {
            $this->assertContains($key, $keys, "Premium block '{$key}' must be visible via plan feature");
        }
    }

    // ── 7. blocksForAgency(null) returns only free blocks ─────────────────────

    public function test_blocks_for_agency_with_null_returns_only_free_blocks(): void
    {
        $blocks = LayoutBlockSchema::blocksForAgency(null);
        $keys = array_map(fn ($b) => $b->getName(), $blocks);

        $this->assertCount(count(self::FREE_BLOCKS), $blocks);

        foreach (self::PREMIUM_BLOCKS as $key) {
            $this->assertNotContains($key, $keys, "Premium block '{$key}' must not appear when agency is null");
        }
    }

    // ── 8. premiumViolation() returns null for free-only blocks ───────────────

    public function test_premium_violation_returns_null_for_free_blocks_only(): void
    {
        $agency = $this->makeAgency();
        $blocks = [
            ['type' => 'hero', 'data' => ['title' => 'Welcome']],
            ['type' => 'cta', 'data' => ['title' => 'Act Now']],
        ];

        $this->assertNull(LayoutBlockSchema::premiumViolation($blocks, $agency));
    }

    // ── 9. premiumViolation() returns null when agency has entitlement ─────────

    public function test_premium_violation_returns_null_when_agency_has_entitlement(): void
    {
        $agency = $this->makeAgency();
        $this->grantPackEntitlement($agency);

        $blocks = [
            ['type' => 'hero', 'data' => []],
            ['type' => 'pricing_table', 'data' => ['tiers' => []]],
            ['type' => 'stats_strip', 'data' => ['stats' => []]],
        ];

        $this->assertNull(LayoutBlockSchema::premiumViolation($blocks, $agency));
    }

    // ── 10. premiumViolation() returns error when no entitlement ──────────────

    public function test_premium_violation_returns_error_when_no_entitlement(): void
    {
        $agency = $this->makeAgency();
        $blocks = [
            ['type' => 'hero', 'data' => []],
            ['type' => 'pricing_table', 'data' => []],
        ];

        $violation = LayoutBlockSchema::premiumViolation($blocks, $agency);

        $this->assertNotNull($violation);
        $this->assertStringContainsString('block_pack_marketing', $violation);
    }

    // ── 11. premiumViolation() returns null when premium block is absent ──────

    public function test_premium_violation_returns_null_when_no_premium_block_in_data(): void
    {
        $agency = $this->makeAgency();
        $blocks = [
            ['type' => 'rich_text', 'data' => ['content' => 'Hello']],
            ['type' => 'spacer', 'data' => ['size' => 'md']],
        ];

        $this->assertNull(LayoutBlockSchema::premiumViolation($blocks, $agency));
    }

    // ── 12. knownTypes() includes premium block keys ───────────────────────────

    public function test_known_types_includes_all_premium_block_keys(): void
    {
        $knownTypes = LayoutBlockSchema::knownTypes();

        foreach (self::PREMIUM_BLOCKS as $key) {
            $this->assertContains($key, $knownTypes, "knownTypes() must include premium block '{$key}' for renderer");
        }
    }

    // ── 13. blocksForAgency() filters revoked entitlement ─────────────────────

    public function test_blocks_for_agency_hides_premium_blocks_when_entitlement_revoked(): void
    {
        $agency = $this->makeAgency();
        $entitlement = $this->grantPackEntitlement($agency);

        // With active entitlement: premium blocks visible
        $keys = array_map(fn ($b) => $b->getName(), LayoutBlockSchema::blocksForAgency($agency));
        $this->assertContains('pricing_table', $keys);

        // Revoke entitlement
        $entitlement->revoke();

        // Need fresh agency instance (reload plan/limits aren't cached here, but
        // FeatureAccessService queries AgencyEntitlement fresh each time — this passes)
        $freshAgency = Agency::find($agency->id);
        $keysAfterRevoke = array_map(fn ($b) => $b->getName(), LayoutBlockSchema::blocksForAgency($freshAgency));
        $this->assertNotContains('pricing_table', $keysAfterRevoke);
    }

    // ── 14. Registry has 12 blocks total ──────────────────────────────────────

    public function test_registry_has_twelve_blocks_total(): void
    {
        $count = count($this->registry()->blocks());
        $expected = count(self::FREE_BLOCKS) + count(self::PREMIUM_BLOCKS);

        $this->assertEquals($expected, $count, "Registry must have {$expected} blocks (7 free + 5 premium)");
    }
}
