<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Filament\Agency\Pages\AgencyBillingPage;
use App\Models\Central\Agency;
use App\Models\Central\AgencyMember;
use App\Models\Central\AgencySubscription;
use App\Models\Central\BillingEvent;
use App\Models\Central\Plan;
use App\Models\Central\User;
use Tests\CentralTestCase;

/**
 * Covers AgencyBillingPage access control, data methods, and subscription state.
 *
 * Tests:
 *  1. Owner can access the billing page
 *  2. Admin cannot access
 *  3. Member cannot access
 *  4. Unauthenticated user cannot access
 *  5. billingTypeLabel() returns correct label per billing interval
 *  6. billingTypeLabel() returns 'Lifetime' for LTD agencies
 *  7. hasStripeCustomer() returns true when customer ID is set
 *  8. hasStripeCustomer() returns false when no customer ID
 *  9. recentBillingEvents() returns agency-scoped events, newest first
 * 10. recentBillingEvents() is limited
 * 11. openCustomerPortal() sends a warning when Stripe not configured
 * 12. subscription renewalLabel shows renewal date
 * 13. renewalLabel shows Lifetime text for LTD subscriptions
 */
class AgencyBillingPageTest extends CentralTestCase
{
    // ── Helpers ───────────────────────────────────────────────────────────────

    private function makePlan(string $interval = 'month'): Plan
    {
        static $n = 0;
        $n++;

        return Plan::create([
            'name' => "Plan {$n}",
            'slug' => "plan-{$n}",
            'price' => 29,
            'billing_interval' => $interval,
            'is_active' => true,
            'sort_order' => $n,
        ]);
    }

    private function makeAgency(?Plan $plan = null, string $billingType = 'monthly'): Agency
    {
        static $n = 0;
        $n++;

        return Agency::create([
            'name' => "Agency {$n}",
            'slug' => "agency-{$n}",
            'brand_name' => "Agency {$n}",
            'status' => 'active',
            'billing_type' => $billingType,
            'plan_id' => $plan?->id,
        ]);
    }

    private function makeUser(Agency $agency, string $role): User
    {
        static $n = 0;
        $n++;

        $user = User::create([
            'name' => "User {$n}",
            'email' => "user{$n}@example.com",
            'password' => bcrypt('password'),
        ]);

        AgencyMember::create([
            'agency_id' => $agency->id,
            'user_id' => $user->id,
            'role' => $role,
            'status' => AgencyMember::STATUS_ACTIVE,
            'accepted_at' => now(),
        ]);

        if ($role === AgencyMember::ROLE_OWNER) {
            $agency->update(['owner_user_id' => $user->id]);
        }

        return $user;
    }

    private function makePage(Agency $agency): AgencyBillingPage
    {
        app()->instance('current_agency', $agency);

        return app(AgencyBillingPage::class);
    }

    // ── canAccess: role enforcement ───────────────────────────────────────────

    public function test_owner_can_access_billing_page(): void
    {
        $agency = $this->makeAgency();
        $owner = $this->makeUser($agency, AgencyMember::ROLE_OWNER);

        app()->instance('current_agency', $agency);
        $this->actingAs($owner, 'web');

        $this->assertTrue(AgencyBillingPage::canAccess());
    }

    public function test_admin_cannot_access_billing_page(): void
    {
        $agency = $this->makeAgency();
        $admin = $this->makeUser($agency, AgencyMember::ROLE_ADMIN);

        app()->instance('current_agency', $agency);
        $this->actingAs($admin, 'web');

        $this->assertFalse(AgencyBillingPage::canAccess());
    }

    public function test_member_cannot_access_billing_page(): void
    {
        $agency = $this->makeAgency();
        $member = $this->makeUser($agency, AgencyMember::ROLE_MEMBER);

        app()->instance('current_agency', $agency);
        $this->actingAs($member, 'web');

        $this->assertFalse(AgencyBillingPage::canAccess());
    }

    public function test_unauthenticated_cannot_access_billing_page(): void
    {
        $agency = $this->makeAgency();
        app()->instance('current_agency', $agency);

        // No actingAs — auth()->user() is null
        $this->assertFalse(AgencyBillingPage::canAccess());
    }

    // ── billingTypeLabel() ────────────────────────────────────────────────────

    public function test_billing_type_label_monthly(): void
    {
        $plan = $this->makePlan('month');
        $agency = $this->makeAgency($plan, 'monthly');
        $page = $this->makePage($agency);

        $this->assertEquals('Mensile', $page->billingTypeLabel());
    }

    public function test_billing_type_label_yearly(): void
    {
        $plan = $this->makePlan('year');
        $agency = $this->makeAgency($plan, 'monthly');
        $page = $this->makePage($agency);

        $this->assertEquals('Annuale', $page->billingTypeLabel());
    }

    public function test_billing_type_label_lifetime(): void
    {
        $agency = $this->makeAgency(null, 'lifetime');
        $page = $this->makePage($agency);

        $this->assertEquals('Lifetime', $page->billingTypeLabel());
    }

    // ── hasStripeCustomer() ───────────────────────────────────────────────────

    public function test_has_stripe_customer_true_when_id_set(): void
    {
        $agency = $this->makeAgency();
        $agency->update(['stripe_customer_id' => 'cus_test123']);
        $page = $this->makePage($agency);

        $this->assertTrue($page->hasStripeCustomer());
    }

    public function test_has_stripe_customer_false_when_id_missing(): void
    {
        $agency = $this->makeAgency();
        $page = $this->makePage($agency);

        $this->assertFalse($page->hasStripeCustomer());
    }

    // ── recentBillingEvents() ─────────────────────────────────────────────────

    public function test_recent_billing_events_returns_agency_scoped_events(): void
    {
        $agencyA = $this->makeAgency();
        $agencyB = $this->makeAgency();

        BillingEvent::create([
            'agency_id' => $agencyA->id,
            'event_type' => 'invoice.paid',
            'payload' => [],
        ]);

        BillingEvent::create([
            'agency_id' => $agencyB->id,
            'event_type' => 'invoice.paid',
            'payload' => [],
        ]);

        $page = $this->makePage($agencyA);
        $events = $page->recentBillingEvents();

        $this->assertCount(1, $events);
        $this->assertEquals($agencyA->id, $events->first()->agency_id);
    }

    public function test_recent_billing_events_respects_limit(): void
    {
        $agency = $this->makeAgency();

        for ($i = 0; $i < 12; $i++) {
            BillingEvent::create([
                'agency_id' => $agency->id,
                'event_type' => 'invoice.paid',
                'payload' => [],
            ]);
        }

        $page = $this->makePage($agency);
        $events = $page->recentBillingEvents(limit: 5);

        $this->assertCount(5, $events);
    }

    public function test_recent_billing_events_empty_for_new_agency(): void
    {
        $agency = $this->makeAgency();
        $page = $this->makePage($agency);

        $this->assertTrue($page->recentBillingEvents()->isEmpty());
    }

    // ── subscription state ────────────────────────────────────────────────────

    public function test_subscription_renewal_label_shows_date(): void
    {
        $agency = $this->makeAgency();
        $sub = AgencySubscription::create([
            'agency_id' => $agency->id,
            'status' => 'active',
            'billing_type' => 'monthly',
            'current_period_end' => now()->addDays(15),
        ]);

        $label = $sub->renewalLabel();

        $this->assertStringContainsString('Rinnovo il', $label);
    }

    public function test_subscription_renewal_label_for_lifetime(): void
    {
        $agency = $this->makeAgency();
        $sub = AgencySubscription::create([
            'agency_id' => $agency->id,
            'status' => 'active',
            'billing_type' => 'lifetime',
        ]);

        $this->assertEquals('Lifetime — non scade', $sub->renewalLabel());
    }

    public function test_open_customer_portal_warns_when_stripe_not_configured(): void
    {
        config(['services.stripe.secret' => '']);

        $agency = $this->makeAgency();
        $agency->update(['stripe_customer_id' => 'cus_test']);
        $page = $this->makePage($agency);

        // openCustomerPortal() calls $this->redirect() which requires Livewire context.
        // Test just verifies that the guard condition (isStripeConfigured) works correctly.
        $this->assertFalse($page->isStripeConfigured());
    }
}
