<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Exceptions\AgencyPlanRequiredException;
use App\Models\Central\Agency;
use App\Models\Central\AgencySubscription;
use App\Models\Central\Plan;
use App\Services\StoreProvisioningGate;
use Tests\CentralTestCase;

/**
 * Covers Agency::hasActivePlan() — the single source of truth for "can this
 * agency create a new store" — and the StoreProvisioningGate service that
 * both the agency wizard (CreateStore) and the central API (TenantController)
 * call to enforce it.
 */
class StoreProvisioningGateTest extends CentralTestCase
{
    private static int $seq = 0;

    private function makeAgency(): Agency
    {
        self::$seq++;

        return Agency::create([
            'name' => 'Gate Agency '.self::$seq,
            'slug' => 'gate-agency-'.self::$seq,
            'brand_name' => 'Gate Agency '.self::$seq,
            'status' => 'active',
            'billing_type' => 'monthly',
        ]);
    }

    private function makePlan(): Plan
    {
        self::$seq++;

        return Plan::create([
            'name' => 'Gate Plan '.self::$seq,
            'slug' => 'gate-plan-'.self::$seq,
            'price' => 49,
            'billing_interval' => 'month',
            'is_active' => true,
            'sort_order' => self::$seq,
        ]);
    }

    private function makeSubscription(Agency $agency, string $status, string $billingType = 'monthly'): AgencySubscription
    {
        return AgencySubscription::create([
            'agency_id' => $agency->id,
            'plan_id' => $agency->plan_id,
            'status' => $status,
            'billing_type' => $billingType,
        ]);
    }

    // ── Agency::hasActivePlan() ─────────────────────────────────────────────

    public function test_agency_without_plan_has_no_active_plan(): void
    {
        $agency = $this->makeAgency();

        $this->assertFalse($agency->hasActivePlan());
    }

    public function test_agency_with_plan_and_no_subscription_row_is_treated_as_active(): void
    {
        // A plan assigned directly by an admin (no Stripe checkout, no
        // AgencySubscription row) must still count as active — plan_id is
        // the explicit signal of intent in that case.
        $agency = $this->makeAgency();
        $plan = $this->makePlan();
        $agency->update(['plan_id' => $plan->id]);

        $this->assertTrue($agency->fresh()->hasActivePlan());
    }

    public function test_agency_with_active_subscription_has_active_plan(): void
    {
        $agency = $this->makeAgency();
        $plan = $this->makePlan();
        $agency->update(['plan_id' => $plan->id]);
        $this->makeSubscription($agency, 'active');

        $this->assertTrue($agency->fresh()->hasActivePlan());
    }

    public function test_agency_with_trialing_subscription_has_active_plan(): void
    {
        $agency = $this->makeAgency();
        $plan = $this->makePlan();
        $agency->update(['plan_id' => $plan->id]);
        $this->makeSubscription($agency, 'trialing');

        $this->assertTrue($agency->fresh()->hasActivePlan());
    }

    public function test_agency_with_lifetime_subscription_has_active_plan(): void
    {
        $agency = $this->makeAgency();
        $plan = $this->makePlan();
        $agency->update(['plan_id' => $plan->id, 'billing_type' => 'lifetime']);
        $this->makeSubscription($agency, 'active', 'lifetime');

        $this->assertTrue($agency->fresh()->hasActivePlan());
    }

    public function test_agency_with_past_due_subscription_has_no_active_plan(): void
    {
        $agency = $this->makeAgency();
        $plan = $this->makePlan();
        $agency->update(['plan_id' => $plan->id]);
        $this->makeSubscription($agency, 'past_due');

        $this->assertFalse($agency->fresh()->hasActivePlan());
    }

    public function test_agency_with_cancelled_subscription_has_no_active_plan(): void
    {
        $agency = $this->makeAgency();
        $plan = $this->makePlan();
        $agency->update(['plan_id' => $plan->id]);
        $this->makeSubscription($agency, 'cancelled');

        $this->assertFalse($agency->fresh()->hasActivePlan());
    }

    // ── StoreProvisioningGate ─────────────────────────────────────────────────

    public function test_gate_allows_agency_with_active_plan(): void
    {
        $agency = $this->makeAgency();
        $plan = $this->makePlan();
        $agency->update(['plan_id' => $plan->id]);
        $this->makeSubscription($agency, 'active');

        $gate = app(StoreProvisioningGate::class);

        $this->assertTrue($gate->check($agency->fresh()));
        $gate->enforce($agency->fresh());
        $this->addToAssertionCount(1); // enforce() did not throw
    }

    public function test_gate_blocks_agency_without_active_plan(): void
    {
        $agency = $this->makeAgency();
        $gate = app(StoreProvisioningGate::class);

        $this->assertFalse($gate->check($agency));

        $this->expectException(AgencyPlanRequiredException::class);
        $gate->enforce($agency);
    }
}
