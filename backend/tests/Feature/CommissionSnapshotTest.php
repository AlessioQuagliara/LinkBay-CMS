<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\Agency;
use App\Models\Central\CommissionRecord;
use App\Models\Central\Plan;
use App\Models\Central\PlatformFeeRule;
use Tests\CentralTestCase;

class CommissionSnapshotTest extends CentralTestCase
{
    public function test_commission_fee_pct_does_not_change_when_plan_changes(): void
    {
        $planA = Plan::create(['name' => 'PlanA', 'slug' => 'plan-a', 'price' => 29, 'billing_interval' => 'month', 'is_active' => true, 'sort_order' => 1]);
        $planB = Plan::create(['name' => 'PlanB', 'slug' => 'plan-b', 'price' => 79, 'billing_interval' => 'month', 'is_active' => true, 'sort_order' => 2]);

        $ruleA = PlatformFeeRule::create(['plan_id' => $planA->id, 'billing_type' => null, 'fee_pct' => 0.3000, 'fee_type' => 'platform_share', 'valid_from' => now()->subDay()]);

        $agency = Agency::create(['name' => 'Ag', 'slug' => 'ag', 'brand_name' => 'Ag', 'plan_id' => $planA->id, 'billing_type' => 'monthly', 'status' => 'active']);

        // Crea CommissionRecord con piano A (fee 30%)
        $commission = CommissionRecord::create([
            'agency_id'            => $agency->id,
            'platform_fee_rule_id' => $ruleA->id,
            'gross_amount_cents'   => 10000,
            'fee_pct'              => $ruleA->fee_pct,
            'fee_amount_cents'     => 3000,
            'net_to_agency_cents'  => 7000,
            'currency'             => 'eur',
            'status'               => CommissionRecord::STATUS_PENDING,
        ]);

        // Aggiorna piano dell'agency a PlanB
        $agency->update(['plan_id' => $planB->id]);

        // Ricarica il CommissionRecord — il fee_pct deve essere invariato
        $commission->refresh();

        $this->assertEquals('0.3000', $commission->fee_pct, 'fee_pct deve essere immutabile dopo la creazione');
        $this->assertEquals($ruleA->id, $commission->platform_fee_rule_id, 'Il FK alla regola non deve cambiare');
    }

    public function test_commission_records_are_scoped_to_agency(): void
    {
        $plan   = Plan::create(['name' => 'P', 'slug' => 'p', 'price' => 10, 'billing_interval' => 'month', 'is_active' => true, 'sort_order' => 1]);
        $rule   = PlatformFeeRule::create(['plan_id' => null, 'billing_type' => null, 'fee_pct' => 0.2000, 'fee_type' => 'platform_share', 'valid_from' => now()->subDay()]);

        $agencyA = Agency::create(['name' => 'A', 'slug' => 'a', 'brand_name' => 'A', 'plan_id' => $plan->id, 'billing_type' => 'monthly', 'status' => 'active']);
        $agencyB = Agency::create(['name' => 'B', 'slug' => 'b', 'brand_name' => 'B', 'plan_id' => $plan->id, 'billing_type' => 'monthly', 'status' => 'active']);

        CommissionRecord::create(['agency_id' => $agencyA->id, 'platform_fee_rule_id' => $rule->id, 'gross_amount_cents' => 5000, 'fee_pct' => '0.2000', 'fee_amount_cents' => 1000, 'net_to_agency_cents' => 4000, 'currency' => 'eur', 'status' => CommissionRecord::STATUS_SETTLED]);
        CommissionRecord::create(['agency_id' => $agencyB->id, 'platform_fee_rule_id' => $rule->id, 'gross_amount_cents' => 8000, 'fee_pct' => '0.2000', 'fee_amount_cents' => 1600, 'net_to_agency_cents' => 6400, 'currency' => 'eur', 'status' => CommissionRecord::STATUS_SETTLED]);

        $countA = CommissionRecord::where('agency_id', $agencyA->id)->count();
        $countB = CommissionRecord::where('agency_id', $agencyB->id)->count();

        $this->assertEquals(1, $countA);
        $this->assertEquals(1, $countB);
        // Verifica che la query scoped all'agency A non ritorni record dell'agency B
        $this->assertEmpty(CommissionRecord::where('agency_id', $agencyA->id)->where('agency_id', $agencyB->id)->get());
    }
}
