<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Jobs\ProcessStripeWebhookJob;
use App\Models\Central\Agency;
use App\Models\Central\AgencySubscription;
use App\Models\Central\BillingEvent;
use App\Models\Central\Plan;
use App\Services\AgencySubscriptionService;
use Illuminate\Support\Facades\Queue;
use Illuminate\Testing\TestResponse;
use Stripe\Invoice;
use Stripe\Subscription;
use Tests\CentralTestCase;

/**
 * Covers the Stripe subscription lifecycle via webhooks and the
 * AgencySubscriptionService.
 *
 * HTTP tests send a raw JSON body with a real HMAC-SHA256 signature so that
 * StripeWebhookController::handle() passes Webhook::constructEvent() validation.
 *
 * Service tests call AgencySubscriptionService directly with Stripe SDK objects
 * constructed from arrays (no API calls needed).
 *
 * Tests:
 *  1. customer.subscription.created → AgencySubscription status='active'
 *  2. invoice.paid → BillingEvent saved (idempotent on same stripe_event_id)
 *  3. customer.subscription.updated (downgrade) → plan_id updated on Agency
 *  4. customer.subscription.deleted → Agency.status='suspended'
 *  5. Webhook with invalid signature → 400
 *  6. Duplicate stripe_event_id → 200, no second BillingEvent row
 *  7. Agency without stripe_customer_id → syncFromStripe throws, handled gracefully
 */
class SubscriptionLifecycleTest extends CentralTestCase
{
    // ── Helpers ───────────────────────────────────────────────────────────────

    private static int $seq = 0;

    private function makePlan(string $priceId = 'price_test', array $limits = []): Plan
    {
        self::$seq++;

        return Plan::create([
            'name' => 'Plan '.self::$seq,
            'slug' => 'plan-'.self::$seq,
            'price' => 49,
            'billing_interval' => 'month',
            'stripe_price_id' => $priceId,
            'is_active' => true,
            'sort_order' => self::$seq,
            'limits' => $limits,
        ]);
    }

    private function makeAgency(?Plan $plan = null, string $customerId = ''): Agency
    {
        self::$seq++;

        $agency = Agency::create([
            'name' => 'Agency '.self::$seq,
            'slug' => 'agency-'.self::$seq,
            'brand_name' => 'Agency '.self::$seq,
            'status' => 'active',
            'billing_type' => 'monthly',
            'stripe_customer_id' => $customerId ?: ('cus_test_'.self::$seq),
        ]);

        if ($plan) {
            $agency->update(['plan_id' => $plan->id]);
            $agency->load('plan');
        }

        return $agency;
    }

    private function makeSubscription(Agency $agency, string $subId, string $status = 'active'): AgencySubscription
    {
        return AgencySubscription::create([
            'agency_id' => $agency->id,
            'stripe_subscription_id' => $subId,
            'stripe_customer_id' => $agency->stripe_customer_id,
            'status' => $status,
            'billing_type' => 'monthly',
        ]);
    }

    /** Build a Stripe Subscription object from an array without API calls. */
    private function makeStripeSubscription(
        string $customerId,
        string $priceId = 'price_test',
        string $status = 'active',
        ?string $subId = null,
    ): Subscription {
        return Subscription::constructFrom([
            'id' => $subId ?? ('sub_test_'.uniqid()),
            'customer' => $customerId,
            'status' => $status,
            'items' => [
                'object' => 'list',
                'data' => [
                    ['id' => 'si_test', 'price' => ['id' => $priceId]],
                ],
            ],
            'current_period_start' => time(),
            'current_period_end' => time() + 2592000,
            'trial_end' => null,
            'canceled_at' => null,
        ]);
    }

    /** Build a Stripe Invoice object from an array without API calls. */
    private function makeStripeInvoice(string $customerId): Invoice
    {
        return Invoice::constructFrom([
            'id' => 'in_test_'.uniqid(),
            'customer' => $customerId,
            'lines' => [
                'object' => 'list',
                'data' => [
                    [
                        'id' => 'il_test',
                        'period' => ['start' => time(), 'end' => time() + 2592000],
                    ],
                ],
            ],
        ]);
    }

    /**
     * Compute a valid Stripe-Signature header for raw JSON payload.
     * Mirrors Stripe's own verification logic (WebhookSignature::verifyHeader).
     */
    private function makeStripeSignature(string $rawPayload, string $secret): string
    {
        $timestamp = time();
        $sig = hash_hmac('sha256', $timestamp.'.'.$rawPayload, $secret);

        return "t={$timestamp},v1={$sig}";
    }

    /**
     * Send a raw JSON POST to the Stripe webhook endpoint with a computed signature.
     * Uses call() instead of postJson() to preserve the exact raw body the HMAC was signed over.
     */
    private function webhookPost(array $event, string $secret = 'test_whsec'): TestResponse
    {
        config(['services.stripe.webhook_secret' => $secret]);

        $raw = json_encode($event);
        $sig = $this->makeStripeSignature($raw, $secret);

        return $this->call(
            'POST',
            route('stripe.webhook'),
            [],
            [],
            [],
            ['HTTP_STRIPE_SIGNATURE' => $sig, 'CONTENT_TYPE' => 'application/json'],
            $raw,
        );
    }

    private function service(): AgencySubscriptionService
    {
        return app(AgencySubscriptionService::class);
    }

    // ── Test 1 ────────────────────────────────────────────────────────────────

    public function test_subscription_created_webhook_upserts_agency_subscription_as_active(): void
    {
        $plan = $this->makePlan('price_starter');
        $agency = $this->makeAgency($plan, 'cus_sub_created');
        $subId = 'sub_created_'.uniqid();

        $stripeSub = $this->makeStripeSubscription('cus_sub_created', 'price_starter', 'active', $subId);

        // ── Call service directly ─────────────────────────────────────────────
        $localSub = $this->service()->syncFromStripe($stripeSub);

        $this->assertEquals('active', $localSub->status);
        $this->assertEquals($agency->id, $localSub->agency_id);
        $this->assertEquals($subId, $localSub->stripe_subscription_id);
    }

    // ── Test 2 ────────────────────────────────────────────────────────────────

    public function test_webhook_billing_event_is_idempotent_on_same_event_id(): void
    {
        Queue::fake();

        $eventId = 'evt_idempotent_'.uniqid();
        $event = [
            'id' => $eventId,
            'type' => 'invoice.paid',
            'data' => ['object' => []],
        ];

        // ── First call inserts BillingEvent ───────────────────────────────────
        $this->webhookPost($event);

        $count = BillingEvent::where('stripe_event_id', $eventId)->count();
        $this->assertEquals(1, $count, 'BillingEvent should be created once');

        // ── Second call with same event_id must not insert a duplicate ─────────
        $this->webhookPost($event);

        $count = BillingEvent::where('stripe_event_id', $eventId)->count();
        $this->assertEquals(1, $count, 'BillingEvent must not be duplicated');
    }

    // ── Test 3 ────────────────────────────────────────────────────────────────

    public function test_subscription_updated_syncs_new_plan_onto_agency(): void
    {
        $oldPlan = $this->makePlan('price_old');
        $newPlan = $this->makePlan('price_new');
        $agency = $this->makeAgency($oldPlan, 'cus_upgrade');
        $subId = 'sub_upgrade_'.uniqid();

        $this->makeSubscription($agency, $subId);

        // ── Webhook carries the new price ID ──────────────────────────────────
        $stripeSub = $this->makeStripeSubscription('cus_upgrade', 'price_new', 'active', $subId);
        $this->service()->syncFromStripe($stripeSub);

        $agency->refresh();

        $this->assertEquals($newPlan->id, $agency->plan_id, 'Agency plan_id should reflect the new price');
    }

    // ── Test 4 ────────────────────────────────────────────────────────────────

    public function test_subscription_deleted_suspends_agency(): void
    {
        $plan = $this->makePlan('price_cancel');
        $agency = $this->makeAgency($plan, 'cus_cancel');
        $subId = 'sub_cancel_'.uniqid();

        $this->makeSubscription($agency, $subId, 'active');

        $stripeSub = $this->makeStripeSubscription('cus_cancel', 'price_cancel', 'canceled', $subId);
        $this->service()->handleDeleted($stripeSub);

        $agency->refresh();

        // ── Agency suspended ──────────────────────────────────────────────────
        $this->assertEquals('suspended', $agency->status);

        // ── Local subscription marked cancelled ───────────────────────────────
        $localSub = AgencySubscription::where('agency_id', $agency->id)->first();
        $this->assertNotNull($localSub);
        $this->assertEquals('cancelled', $localSub->status);
        $this->assertNotNull($localSub->cancelled_at);
    }

    // ── Test 5 ────────────────────────────────────────────────────────────────

    public function test_webhook_with_invalid_signature_returns_400(): void
    {
        config(['services.stripe.webhook_secret' => 'correct_secret']);

        $raw = json_encode(['id' => 'evt_bad', 'type' => 'ping', 'data' => ['object' => []]]);

        // ── Compute signature with a WRONG secret ─────────────────────────────
        $badSig = $this->makeStripeSignature($raw, 'wrong_secret');

        $response = $this->call(
            'POST',
            route('stripe.webhook'),
            [],
            [],
            [],
            ['HTTP_STRIPE_SIGNATURE' => $badSig, 'CONTENT_TYPE' => 'application/json'],
            $raw,
        );

        $response->assertStatus(400);
    }

    // ── Test 6 ────────────────────────────────────────────────────────────────

    public function test_already_processed_event_returns_200_without_reprocessing(): void
    {
        Queue::fake();

        $eventId = 'evt_already_done_'.uniqid();

        // ── Seed a BillingEvent that is already processed ─────────────────────
        BillingEvent::create([
            'stripe_event_id' => $eventId,
            'event_type' => 'invoice.paid',
            'payload' => json_encode([]),
            'processed_at' => now(),
        ]);

        $event = [
            'id' => $eventId,
            'type' => 'invoice.paid',
            'data' => ['object' => []],
        ];

        $response = $this->webhookPost($event);

        $response->assertStatus(200);

        // ── No new job dispatched for already-processed event ─────────────────
        Queue::assertNotPushed(ProcessStripeWebhookJob::class);
    }

    // ── Test 7 ────────────────────────────────────────────────────────────────

    public function test_sync_throws_runtime_exception_for_unknown_stripe_customer(): void
    {
        // Stripe customer ID that has no matching Agency
        $stripeSub = $this->makeStripeSubscription('cus_unknown_xyz', 'price_test', 'active');

        $this->expectException(\RuntimeException::class);
        $this->expectExceptionMessageMatches('/Agency not found/');

        $this->service()->syncFromStripe($stripeSub);
    }

    public function test_deleted_subscription_for_unknown_customer_does_not_throw(): void
    {
        // handleDeleted logs a warning and returns early — must not throw
        $stripeSub = $this->makeStripeSubscription('cus_nobody', 'price_test', 'canceled');

        $this->service()->handleDeleted($stripeSub);

        $this->assertTrue(true, 'handleDeleted() should handle missing agency gracefully');
    }

    // ── Invoice paid: agency reactivated ─────────────────────────────────────

    public function test_invoice_paid_reactivates_suspended_agency(): void
    {
        $plan = $this->makePlan('price_active');
        $agency = $this->makeAgency($plan, 'cus_reactivate');
        $agency->update(['status' => 'suspended']);

        $this->makeSubscription($agency, 'sub_reactivate', 'past_due');

        $invoice = $this->makeStripeInvoice('cus_reactivate');
        $this->service()->handleInvoicePaid($invoice);

        $agency->refresh();

        $this->assertEquals('active', $agency->status, 'Agency should be reactivated after invoice paid');

        $localSub = AgencySubscription::where('agency_id', $agency->id)->first();
        $this->assertEquals('active', $localSub->status);
    }
}
