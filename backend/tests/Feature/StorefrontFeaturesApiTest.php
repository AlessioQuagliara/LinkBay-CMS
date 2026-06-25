<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\Agency;
use App\Models\Central\AgencyEntitlement;
use App\Models\Central\Plan;
use App\Models\Central\PluginCatalogItem;
use App\Plugins\MarketingBlockPack\MarketingBlockPackServiceProvider;
use Illuminate\Support\Facades\DB;
use Tests\CentralTestCase;

/**
 * Storefront Features API test suite.
 *
 * Endpoint: GET /api/storefront/{tenantId}/features
 *
 * Tests:
 *  1.  Valid tenant returns 200 with features + meta
 *  2.  Unknown tenant returns 404 with tenant_not_found error
 *  3.  Tenant with no agency returns 404 with agency_not_found error
 *  4.  Feature active via plan → true in response
 *  5.  Feature active via entitlement → true in response
 *  6.  Feature absent (no plan, no entitlement) → false in response
 *  7.  Cross-tenant scoping: different tenants see their own agency's features
 *  8.  Response contains meta.tenant_id and meta.agency_id correctly
 *  9.  No sensitive data exposed (no plan details, no entitlement records)
 * 10.  Revoked entitlement → feature is false
 */
class StorefrontFeaturesApiTest extends CentralTestCase
{
    private static int $seq = 0;

    // ── Helpers ───────────────────────────────────────────────────────────────

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

    /**
     * Raw insert to avoid stancl/tenancy DB-provisioning hooks.
     */
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

    private function makeCatalogItem(string $code): PluginCatalogItem
    {
        return PluginCatalogItem::firstOrCreate(
            ['code' => $code],
            [
                'type' => PluginCatalogItem::TYPE_BLOCK_PACK,
                'name' => ucwords(str_replace('_', ' ', $code)),
                'status' => PluginCatalogItem::STATUS_ACTIVE,
            ]
        );
    }

    private function grantEntitlement(Agency $agency, string $code, string $status = AgencyEntitlement::STATUS_ACTIVE): AgencyEntitlement
    {
        $item = $this->makeCatalogItem($code);

        return AgencyEntitlement::create([
            'agency_id' => $agency->id,
            'catalog_item_id' => $item->id,
            'source' => AgencyEntitlement::SOURCE_MANUAL,
            'status' => $status,
        ]);
    }

    private function url(string $tenantId): string
    {
        return "/api/storefront/{$tenantId}/features";
    }

    // ── 1. Valid tenant → 200 ─────────────────────────────────────────────────

    public function test_valid_tenant_returns_200_with_features_and_meta(): void
    {
        $agency = $this->makeAgency();
        $tenantId = $this->makeTenant($agency);

        $response = $this->getJson($this->url($tenantId));

        $response->assertOk()
            ->assertJsonStructure(['features', 'meta' => ['tenant_id', 'agency_id']]);
    }

    // ── 2. Unknown tenant → 404 ───────────────────────────────────────────────

    public function test_unknown_tenant_returns_404(): void
    {
        $this->getJson($this->url('nonexistent-tenant-xyz'))
            ->assertNotFound()
            ->assertJsonFragment(['error' => 'tenant_not_found']);
    }

    // ── 3. Tenant with no agency → 404 ───────────────────────────────────────

    public function test_tenant_without_agency_returns_404(): void
    {
        self::$seq++;
        $id = 'orphan-'.self::$seq;

        DB::connection('central')->table('tenants')->insert([
            'id' => $id,
            'name' => 'Orphan Store',
            'status' => 'active',
            'agency_id' => null,
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        $this->getJson($this->url($id))
            ->assertNotFound()
            ->assertJsonFragment(['error' => 'agency_not_found']);
    }

    // ── 4. Feature active via plan → true ────────────────────────────────────

    public function test_feature_active_via_plan_returns_true(): void
    {
        $plan = $this->makePlan([MarketingBlockPackServiceProvider::FEATURE_CODE => true]);
        $agency = $this->makeAgency($plan);
        $tenantId = $this->makeTenant($agency);

        $response = $this->getJson($this->url($tenantId));

        $response->assertOk()
            ->assertJsonPath('features.'.MarketingBlockPackServiceProvider::FEATURE_CODE, true);
    }

    // ── 5. Feature active via entitlement → true ──────────────────────────────

    public function test_feature_active_via_entitlement_returns_true(): void
    {
        $agency = $this->makeAgency(); // no plan
        $tenantId = $this->makeTenant($agency);
        $this->grantEntitlement($agency, MarketingBlockPackServiceProvider::FEATURE_CODE);

        $response = $this->getJson($this->url($tenantId));

        $response->assertOk()
            ->assertJsonPath('features.'.MarketingBlockPackServiceProvider::FEATURE_CODE, true);
    }

    // ── 6. Feature absent → false ─────────────────────────────────────────────

    public function test_feature_absent_without_plan_or_entitlement_returns_false(): void
    {
        $agency = $this->makeAgency(); // no plan, no entitlements
        $tenantId = $this->makeTenant($agency);

        $response = $this->getJson($this->url($tenantId));

        $response->assertOk()
            ->assertJsonPath('features.'.MarketingBlockPackServiceProvider::FEATURE_CODE, false);
    }

    // ── 7. Cross-tenant scoping ───────────────────────────────────────────────

    public function test_features_are_scoped_to_each_tenants_own_agency(): void
    {
        $plan = $this->makePlan([MarketingBlockPackServiceProvider::FEATURE_CODE => true]);

        $agencyA = $this->makeAgency($plan);  // has the feature
        $agencyB = $this->makeAgency();        // does not have the feature

        $tenantA = $this->makeTenant($agencyA);
        $tenantB = $this->makeTenant($agencyB);

        $this->getJson($this->url($tenantA))
            ->assertJsonPath('features.'.MarketingBlockPackServiceProvider::FEATURE_CODE, true);

        $this->getJson($this->url($tenantB))
            ->assertJsonPath('features.'.MarketingBlockPackServiceProvider::FEATURE_CODE, false);
    }

    // ── 8. Meta fields ────────────────────────────────────────────────────────

    public function test_meta_contains_correct_tenant_and_agency_ids(): void
    {
        $agency = $this->makeAgency();
        $tenantId = $this->makeTenant($agency);

        $response = $this->getJson($this->url($tenantId));

        $response->assertOk()
            ->assertJsonPath('meta.tenant_id', $tenantId)
            ->assertJsonPath('meta.agency_id', $agency->id);
    }

    // ── 9. No sensitive data exposed ──────────────────────────────────────────

    public function test_response_does_not_expose_sensitive_data(): void
    {
        $plan = $this->makePlan(['block_pack_marketing' => true, 'max_stores' => 5]);
        $agency = $this->makeAgency($plan);
        $tenantId = $this->makeTenant($agency);

        $json = $this->getJson($this->url($tenantId))->json();

        // Only top-level keys must be features and meta
        $this->assertEqualsCanonicalizing(['features', 'meta'], array_keys($json));

        // Meta must not contain plan details, billing info, or stripe keys
        $metaKeys = array_keys($json['meta']);
        $this->assertNotContains('plan', $metaKeys);
        $this->assertNotContains('stripe_customer_id', $metaKeys);
        $this->assertNotContains('billing_type', $metaKeys);
    }

    // ── 10. Revoked entitlement → false ──────────────────────────────────────

    public function test_revoked_entitlement_returns_false_for_feature(): void
    {
        $agency = $this->makeAgency();
        $tenantId = $this->makeTenant($agency);
        $this->grantEntitlement($agency, MarketingBlockPackServiceProvider::FEATURE_CODE, AgencyEntitlement::STATUS_REVOKED);

        $this->getJson($this->url($tenantId))
            ->assertOk()
            ->assertJsonPath('features.'.MarketingBlockPackServiceProvider::FEATURE_CODE, false);
    }
}
