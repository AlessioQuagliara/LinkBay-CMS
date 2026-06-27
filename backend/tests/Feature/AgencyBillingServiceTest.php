<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\Agency;
use App\Models\Central\AgencyInvoice;
use App\Models\Central\Plan;
use App\Services\AgencyBillingService;
use Tests\CentralTestCase;

/**
 * Tests AgencyBillingService business logic without live Stripe calls.
 * Stripe calls are covered by integration tests (require real test keys).
 *
 *  1.  createOrRetrieveCustomer() returns existing ID without calling Stripe
 *  2.  cancelSubscription() throws when no stripe_subscription_id
 *  3.  resumeSubscription() throws when no stripe_subscription_id
 *  4.  changeSubscriptionPlan() throws when no stripe_subscription_id
 *  5.  listInvoices() returns agency-scoped records, newest first
 *  6.  listInvoices() returns empty for agency with no invoices
 *  7.  getUpcomingInvoice() returns zero-filled shape when no customer
 *  8.  syncSubscriptionFromStripe() updates stripe_status and subscription_ends_at
 *  9.  syncSubscriptionFromStripe() handles trial_end timestamp
 * 10.  upsertInvoice() creates AgencyInvoice record
 * 11.  upsertInvoice() is idempotent on same stripe_invoice_id
 * 12.  Agency::hasActiveSubscription() reflects stripe_status correctly
 * 13.  Agency::paymentMethodLabel() formats last4 + brand
 * 14.  Agency::paymentMethodLabel() returns '—' when not set
 * 15.  Plan::stripePriceFor() resolves interval to correct price ID
 */
class AgencyBillingServiceTest extends CentralTestCase
{
    private static int $seq = 0;

    private function makeAgency(array $overrides = []): Agency
    {
        self::$seq++;

        return Agency::create(array_merge([
            'name' => 'Agency '.self::$seq,
            'slug' => 'agency-'.self::$seq,
            'brand_name' => 'Agency '.self::$seq,
            'status' => 'active',
            'billing_type' => 'monthly',
        ], $overrides));
    }

    private function makePlan(array $overrides = []): Plan
    {
        self::$seq++;

        return Plan::create(array_merge([
            'name' => 'Plan '.self::$seq,
            'slug' => 'plan-'.self::$seq,
            'price' => 29.00,
            'billing_interval' => 'month',
            'is_active' => true,
            'sort_order' => self::$seq,
        ], $overrides));
    }

    private function service(): AgencyBillingService
    {
        return new AgencyBillingService;
    }

    // ── createOrRetrieveCustomer ──────────────────────────────────────────────

    public function test_returns_existing_customer_id_without_calling_stripe(): void
    {
        $agency = $this->makeAgency(['stripe_customer_id' => 'cus_existing']);

        // If Stripe were invoked, it would fail without a valid key
        config(['services.stripe.secret' => '']);

        $result = $this->service()->createOrRetrieveCustomer($agency);

        $this->assertSame('cus_existing', $result);
    }

    // ── cancelSubscription ────────────────────────────────────────────────────

    public function test_cancel_subscription_throws_when_no_subscription_id(): void
    {
        $agency = $this->makeAgency();

        $this->expectException(\RuntimeException::class);
        $this->expectExceptionMessageMatches('/no active Stripe subscription/');

        $this->service()->cancelSubscription($agency);
    }

    // ── resumeSubscription ────────────────────────────────────────────────────

    public function test_resume_subscription_throws_when_no_subscription_id(): void
    {
        $agency = $this->makeAgency();

        $this->expectException(\RuntimeException::class);
        $this->expectExceptionMessageMatches('/no Stripe subscription to resume/');

        $this->service()->resumeSubscription($agency);
    }

    // ── changeSubscriptionPlan ────────────────────────────────────────────────

    public function test_change_plan_throws_when_no_subscription_id(): void
    {
        $agency = $this->makeAgency();
        $plan = $this->makePlan();

        $this->expectException(\RuntimeException::class);
        $this->expectExceptionMessageMatches('/no active Stripe subscription to change/');

        $this->service()->changeSubscriptionPlan($agency, $plan);
    }

    // ── listInvoices ──────────────────────────────────────────────────────────

    public function test_list_invoices_returns_agency_scoped_records(): void
    {
        $agency1 = $this->makeAgency();
        $agency2 = $this->makeAgency();

        AgencyInvoice::create([
            'agency_id' => $agency1->id,
            'stripe_invoice_id' => 'in_aaa',
            'amount_due' => 2900,
            'amount_paid' => 2900,
            'currency' => 'eur',
            'status' => 'paid',
        ]);

        AgencyInvoice::create([
            'agency_id' => $agency2->id,
            'stripe_invoice_id' => 'in_bbb',
            'amount_due' => 2900,
            'amount_paid' => 2900,
            'currency' => 'eur',
            'status' => 'paid',
        ]);

        $invoices = $this->service()->listInvoices($agency1);

        $this->assertCount(1, $invoices);
        $this->assertSame('in_aaa', $invoices->first()->stripe_invoice_id);
    }

    public function test_list_invoices_returns_empty_for_new_agency(): void
    {
        $agency = $this->makeAgency();

        $this->assertTrue($this->service()->listInvoices($agency)->isEmpty());
    }

    // ── getUpcomingInvoice ─────────────────────────────────────────────────────

    public function test_upcoming_invoice_returns_empty_shape_when_no_customer(): void
    {
        $agency = $this->makeAgency();

        $result = $this->service()->getUpcomingInvoice($agency);

        $this->assertSame(0, $result['amount_due']);
        $this->assertNull($result['next_payment_attempt']);
        $this->assertSame([], $result['lines']);
    }

    // ── syncSubscriptionFromStripe ────────────────────────────────────────────

    public function test_sync_subscription_updates_stripe_status_and_dates(): void
    {
        $agency = $this->makeAgency();
        $periodEnd = now()->addDays(30);

        $fakeSub = (object) [
            'id' => 'sub_sync_test',
            'customer' => 'cus_sync_test',
            'status' => 'active',
            'trial_end' => null,
            'current_period_end' => $periodEnd->timestamp,
            'default_payment_method' => null,
        ];

        $this->service()->syncSubscriptionFromStripe($agency, $fakeSub);

        $fresh = $agency->fresh();

        $this->assertSame('sub_sync_test', $fresh->stripe_subscription_id);
        $this->assertSame('active', $fresh->stripe_status);
        $this->assertSame('cus_sync_test', $fresh->stripe_customer_id);
        $this->assertNotNull($fresh->subscription_ends_at);
    }

    public function test_sync_subscription_sets_trial_ends_at(): void
    {
        $agency = $this->makeAgency();
        $trialEnd = now()->addDays(14);

        $fakeSub = (object) [
            'id' => 'sub_trial',
            'customer' => 'cus_trial',
            'status' => 'trialing',
            'trial_end' => $trialEnd->timestamp,
            'current_period_end' => $trialEnd->timestamp,
            'default_payment_method' => null,
        ];

        $this->service()->syncSubscriptionFromStripe($agency, $fakeSub);

        $fresh = $agency->fresh();

        $this->assertSame('trialing', $fresh->stripe_status);
        $this->assertNotNull($fresh->trial_ends_at);
    }

    // ── upsertInvoice ─────────────────────────────────────────────────────────

    public function test_upsert_invoice_creates_record(): void
    {
        $agency = $this->makeAgency();
        $now = now();

        $fakeInvoice = (object) [
            'id' => 'in_newone',
            'amount_due' => 2900,
            'amount_paid' => 2900,
            'currency' => 'eur',
            'status' => 'paid',
            'invoice_pdf' => 'https://example.com/invoice.pdf',
            'period_start' => $now->timestamp,
            'period_end' => $now->addMonth()->timestamp,
            'lines' => (object) ['data' => []],
            'status_transitions' => (object) ['paid_at' => $now->timestamp],
        ];

        $invoice = $this->service()->upsertInvoice($agency, $fakeInvoice);

        $this->assertInstanceOf(AgencyInvoice::class, $invoice);
        $this->assertSame('in_newone', $invoice->stripe_invoice_id);
        $this->assertSame($agency->id, $invoice->agency_id);
        $this->assertSame('paid', $invoice->status);
    }

    public function test_upsert_invoice_is_idempotent(): void
    {
        $agency = $this->makeAgency();
        $now = now();

        $fakeInvoice = (object) [
            'id' => 'in_idempotent',
            'amount_due' => 2900,
            'amount_paid' => 2900,
            'currency' => 'eur',
            'status' => 'paid',
            'invoice_pdf' => null,
            'period_start' => $now->timestamp,
            'period_end' => $now->addMonth()->timestamp,
            'lines' => (object) ['data' => []],
            'status_transitions' => null,
        ];

        $this->service()->upsertInvoice($agency, $fakeInvoice);
        $this->service()->upsertInvoice($agency, $fakeInvoice);

        $this->assertSame(1, AgencyInvoice::where('stripe_invoice_id', 'in_idempotent')->count());
    }

    // ── Agency helpers ────────────────────────────────────────────────────────

    public function test_agency_has_active_subscription_is_true_for_active_and_trialing(): void
    {
        $active = $this->makeAgency(['stripe_status' => 'active']);
        $trialing = $this->makeAgency(['stripe_status' => 'trialing']);
        $canceled = $this->makeAgency(['stripe_status' => 'canceled']);
        $none = $this->makeAgency();

        $this->assertTrue($active->hasActiveSubscription());
        $this->assertTrue($trialing->hasActiveSubscription());
        $this->assertFalse($canceled->hasActiveSubscription());
        $this->assertFalse($none->hasActiveSubscription());
    }

    public function test_payment_method_label_formats_correctly(): void
    {
        $agency = $this->makeAgency([
            'payment_method_last4' => '4242',
            'payment_method_brand' => 'visa',
        ]);

        $this->assertSame('Visa •••• 4242', $agency->paymentMethodLabel());
    }

    public function test_payment_method_label_returns_dash_when_not_set(): void
    {
        $agency = $this->makeAgency();

        $this->assertSame('—', $agency->paymentMethodLabel());
    }

    // ── Plan helpers ──────────────────────────────────────────────────────────

    public function test_plan_stripe_price_for_interval(): void
    {
        $plan = $this->makePlan([
            'stripe_price_id' => 'price_legacy',
            'stripe_price_id_monthly' => 'price_monthly',
            'stripe_price_id_yearly' => 'price_yearly',
        ]);

        $this->assertSame('price_monthly', $plan->stripePriceFor('monthly'));
        $this->assertSame('price_yearly', $plan->stripePriceFor('yearly'));
        $this->assertSame('price_legacy', $plan->stripePriceFor('unknown'));
    }

    public function test_plan_stripe_price_falls_back_to_legacy_when_monthly_null(): void
    {
        $plan = $this->makePlan([
            'stripe_price_id' => 'price_legacy',
            'stripe_price_id_monthly' => null,
        ]);

        $this->assertSame('price_legacy', $plan->stripePriceFor('monthly'));
    }
}
