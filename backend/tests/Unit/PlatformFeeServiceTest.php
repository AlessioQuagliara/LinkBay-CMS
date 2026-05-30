<?php

declare(strict_types=1);

namespace Tests\Unit;

use App\Models\Central\Agency;
use App\Models\Central\Plan;
use App\Models\Central\PlatformFeeRule;
use App\Services\PlatformFeeService;
use Carbon\Carbon;
use RuntimeException;
use Tests\CentralTestCase;

class PlatformFeeServiceTest extends CentralTestCase
{
    private PlatformFeeService $service;

    protected function setUp(): void
    {
        parent::setUp();
        $this->service = new PlatformFeeService();
    }

    public function test_resolves_plan_specific_rule(): void
    {
        $plan   = Plan::create(['name' => 'Starter', 'slug' => 'starter', 'price' => 29, 'billing_interval' => 'month', 'is_active' => true, 'sort_order' => 1]);
        $agency = Agency::create(['name' => 'Ag', 'slug' => 'ag', 'brand_name' => 'Ag', 'plan_id' => $plan->id, 'billing_type' => 'monthly', 'status' => 'active']);

        // Regola globale con fee 50% (non deve vincere)
        PlatformFeeRule::create(['plan_id' => null, 'billing_type' => null, 'fee_pct' => 0.5000, 'fee_type' => 'platform_share', 'valid_from' => now()->subDay()]);

        // Regola plan-specific con fee 30% (deve vincere)
        PlatformFeeRule::create(['plan_id' => $plan->id, 'billing_type' => null, 'fee_pct' => 0.3000, 'fee_type' => 'platform_share', 'valid_from' => now()->subDay()]);

        $rule = $this->service->resolveRule($agency);

        $this->assertEquals('0.3000', $rule->fee_pct);
    }

    public function test_resolves_global_fallback_when_no_plan_specific_rule(): void
    {
        $plan   = Plan::create(['name' => 'Pro', 'slug' => 'pro', 'price' => 79, 'billing_interval' => 'month', 'is_active' => true, 'sort_order' => 2]);
        $agency = Agency::create(['name' => 'AgPro', 'slug' => 'ag-pro', 'brand_name' => 'AgPro', 'plan_id' => $plan->id, 'billing_type' => 'monthly', 'status' => 'active']);

        // Solo fallback globale
        PlatformFeeRule::create(['plan_id' => null, 'billing_type' => null, 'fee_pct' => 0.2500, 'fee_type' => 'platform_share', 'valid_from' => now()->subDay()]);

        $rule = $this->service->resolveRule($agency);

        $this->assertEquals('0.2500', $rule->fee_pct);
    }

    public function test_resolves_lifetime_billing_type_rule(): void
    {
        $plan   = Plan::create(['name' => 'LTD', 'slug' => 'lifetime-ltd', 'price' => 0, 'billing_interval' => 'month', 'is_active' => true, 'sort_order' => 4]);
        $agency = Agency::create(['name' => 'AgLTD', 'slug' => 'ag-ltd', 'brand_name' => 'AgLTD', 'plan_id' => $plan->id, 'billing_type' => 'lifetime', 'status' => 'active']);

        // Regola per billing_type = lifetime (deve vincere)
        PlatformFeeRule::create(['plan_id' => $plan->id, 'billing_type' => 'lifetime', 'fee_pct' => 0.3800, 'fee_type' => 'platform_share', 'valid_from' => now()->subDay()]);

        // Regola plan-specific senza billing_type specifico
        PlatformFeeRule::create(['plan_id' => $plan->id, 'billing_type' => null, 'fee_pct' => 0.2000, 'fee_type' => 'platform_share', 'valid_from' => now()->subDay()]);

        $rule = $this->service->resolveRule($agency);

        $this->assertEquals('0.3800', $rule->fee_pct);
    }

    public function test_throws_when_no_rule_exists(): void
    {
        $plan   = Plan::create(['name' => 'Mystery', 'slug' => 'mystery', 'price' => 0, 'billing_interval' => 'month', 'is_active' => true, 'sort_order' => 9]);
        $agency = Agency::create(['name' => 'AgMystery', 'slug' => 'ag-mystery', 'brand_name' => 'AgMystery', 'plan_id' => $plan->id, 'billing_type' => 'monthly', 'status' => 'active']);

        $this->expectException(RuntimeException::class);

        $this->service->resolveRule($agency);
    }

    public function test_respects_valid_until_expiry(): void
    {
        $plan   = Plan::create(['name' => 'ExpiredPlan', 'slug' => 'expired', 'price' => 0, 'billing_interval' => 'month', 'is_active' => true, 'sort_order' => 9]);
        $agency = Agency::create(['name' => 'AgExp', 'slug' => 'ag-exp', 'brand_name' => 'AgExp', 'plan_id' => $plan->id, 'billing_type' => 'monthly', 'status' => 'active']);

        // Regola scaduta ieri
        PlatformFeeRule::create(['plan_id' => $plan->id, 'billing_type' => null, 'fee_pct' => 0.9999, 'fee_type' => 'platform_share', 'valid_from' => now()->subMonth(), 'valid_until' => now()->subDay()]);

        // Regola attiva
        PlatformFeeRule::create(['plan_id' => null, 'billing_type' => null, 'fee_pct' => 0.1500, 'fee_type' => 'platform_share', 'valid_from' => now()->subDay()]);

        $rule = $this->service->resolveRule($agency);

        $this->assertEquals('0.1500', $rule->fee_pct);
    }

    public function test_calculate_fee_rounds_correctly(): void
    {
        $rule = new PlatformFeeRule(['fee_pct' => '0.3000']);

        $this->assertEquals(30, $this->service->calculateFee(100, $rule));
        $this->assertEquals(30, $this->service->calculateFee(99, $rule));   // 29.7 → 30 arrotondato
        $this->assertEquals(0, $this->service->calculateFee(0, $rule));
        $this->assertEquals(1900, $this->service->calculateFee(6333, $rule)); // 1899.9 → 1900
    }
}
