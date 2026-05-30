<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\Agency;
use App\Models\Central\AgencySubscription;
use App\Models\Central\Plan;
use App\Services\AgencySubscriptionService;
use Tests\CentralTestCase;

class AgencySubscriptionTest extends CentralTestCase
{
    private AgencySubscriptionService $service;

    protected function setUp(): void
    {
        parent::setUp();
        $this->service = new AgencySubscriptionService();
    }

    public function test_handleDeleted_suspends_agency_and_sets_cancelled(): void
    {
        $plan = Plan::create(['name' => 'Sub', 'slug' => 'sub', 'price' => 29, 'billing_interval' => 'month', 'is_active' => true, 'sort_order' => 1]);

        $agency = Agency::create([
            'name'               => 'SubAg',
            'slug'               => 'sub-ag',
            'brand_name'         => 'SubAg',
            'plan_id'            => $plan->id,
            'billing_type'       => 'monthly',
            'status'             => 'active',
            'stripe_customer_id' => 'cus_test_sub',
        ]);

        AgencySubscription::create([
            'agency_id'    => $agency->id,
            'plan_id'      => $plan->id,
            'status'       => 'active',
            'billing_type' => 'monthly',
        ]);

        // Simula il webhook customer.subscription.deleted
        $fakeStripeSub = \Stripe\Subscription::constructFrom([
            'id'       => 'sub_test_123',
            'customer' => 'cus_test_sub',
            'status'   => 'canceled',
            'items'    => ['data' => []],
        ]);

        $this->service->handleDeleted($fakeStripeSub);

        $agency->refresh();
        $sub = AgencySubscription::where('agency_id', $agency->id)->first();

        $this->assertEquals('suspended', $agency->status, 'Agency deve essere sospesa');
        $this->assertEquals('cancelled', $sub->status, 'AgencySubscription deve essere cancelled');
        $this->assertNotNull($sub->cancelled_at, 'cancelled_at deve essere valorizzato');
    }

    public function test_handleDeleted_is_noop_when_agency_not_found(): void
    {
        $fakeStripeSub = \Stripe\Subscription::constructFrom([
            'id'       => 'sub_not_existing',
            'customer' => 'cus_unknown_xyz',
            'status'   => 'canceled',
            'items'    => ['data' => []],
        ]);

        // Non deve lanciare eccezioni
        $this->service->handleDeleted($fakeStripeSub);

        $this->assertTrue(true); // arrivati qui senza eccezioni
    }

    public function test_createLifetime_creates_non_expiring_subscription(): void
    {
        $plan = Plan::create(['name' => 'LTD', 'slug' => 'ltd', 'price' => 0, 'billing_interval' => 'month', 'is_active' => true, 'sort_order' => 4]);

        $agency = Agency::create([
            'name'         => 'LTDAg',
            'slug'         => 'ltd-ag',
            'brand_name'   => 'LTDAg',
            'plan_id'      => $plan->id,
            'billing_type' => 'lifetime',
            'status'       => 'active',
        ]);

        $sub = $this->service->createLifetime($agency);

        $this->assertEquals('active', $sub->status);
        $this->assertEquals('lifetime', $sub->billing_type);
        $this->assertNull($sub->current_period_end, 'Lifetime non ha scadenza');
        $this->assertNull($sub->stripe_subscription_id, 'Lifetime non ha Stripe subscription ID');
    }
}
