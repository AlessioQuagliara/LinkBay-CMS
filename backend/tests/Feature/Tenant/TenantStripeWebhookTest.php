<?php

declare(strict_types=1);

namespace Tests\Feature\Tenant;

use App\Models\Tenant\Order;
use Illuminate\Testing\TestResponse;
use Tests\Concerns\InteractsWithTenantRoutes;
use Tests\TenantTestCase;

/**
 * Exercises the tenant-scoped Stripe webhook (routes/tenant.php ->
 * TenantStripeWebhookController) end-to-end: real Stripe-Signature header
 * verification (Stripe\Webhook::constructEvent is pure local HMAC/JSON, no
 * network call), routed through the actual controller and DB writes.
 */
class TenantStripeWebhookTest extends TenantTestCase
{
    use InteractsWithTenantRoutes;

    private const SECRET = 'whsec_test_tenant_secret';

    protected function setUp(): void
    {
        parent::setUp();
        $this->bypassTenantDomainResolution();
        config(['services.stripe.tenant_webhook_secret' => self::SECRET]);
    }

    private function postSignedWebhook(array $event): TestResponse
    {
        $payload = json_encode($event);
        $timestamp = time();
        $signature = hash_hmac('sha256', "{$timestamp}.{$payload}", self::SECRET);
        $header = "t={$timestamp},v1={$signature}";

        return $this->call('POST', '/webhooks/stripe', [], [], [], [
            'CONTENT_TYPE' => 'application/json',
            'HTTP_Stripe-Signature' => $header,
        ], $payload);
    }

    private function order(array $overrides = []): Order
    {
        return Order::factory()->create(array_merge([
            'payment_status' => Order::PAYMENT_STATUS_PENDING,
        ], $overrides));
    }

    public function test_rejects_payload_with_invalid_signature(): void
    {
        $response = $this->call('POST', '/webhooks/stripe', [], [], [], [
            'CONTENT_TYPE' => 'application/json',
            'HTTP_Stripe-Signature' => 't=123,v1=not-a-real-signature',
        ], json_encode(['id' => 'evt_1', 'type' => 'payment_intent.succeeded', 'data' => ['object' => []]]));

        $response->assertStatus(400);
    }

    public function test_payment_intent_succeeded_marks_order_paid_and_stores_charge_id(): void
    {
        $order = $this->order(['stripe_payment_intent_id' => 'pi_123']);

        $response = $this->postSignedWebhook([
            'id' => 'evt_1',
            'type' => 'payment_intent.succeeded',
            'data' => ['object' => [
                'id' => 'pi_123',
                'object' => 'payment_intent',
                'latest_charge' => 'ch_123',
            ]],
        ]);

        $response->assertOk();
        $fresh = $order->fresh();
        $this->assertSame(Order::PAYMENT_STATUS_PAID, $fresh->payment_status);
        $this->assertSame('ch_123', $fresh->stripe_charge_id);
        $this->assertNotNull($fresh->captured_at);
    }

    public function test_payment_intent_failed_marks_order_failed(): void
    {
        $order = $this->order(['stripe_payment_intent_id' => 'pi_456']);

        $response = $this->postSignedWebhook([
            'id' => 'evt_2',
            'type' => 'payment_intent.payment_failed',
            'data' => ['object' => [
                'id' => 'pi_456',
                'object' => 'payment_intent',
            ]],
        ]);

        $response->assertOk();
        $this->assertSame(Order::PAYMENT_STATUS_FAILED, $order->fresh()->payment_status);
    }

    public function test_charge_refunded_marks_full_refund_when_amount_covers_total(): void
    {
        $order = $this->order([
            'stripe_charge_id' => 'ch_789',
            'total' => 50,
            'payment_status' => Order::PAYMENT_STATUS_PAID,
        ]);

        $response = $this->postSignedWebhook([
            'id' => 'evt_3',
            'type' => 'charge.refunded',
            'data' => ['object' => [
                'id' => 'ch_789',
                'object' => 'charge',
                'amount_refunded' => 5000,
            ]],
        ]);

        $response->assertOk();
        $fresh = $order->fresh();
        $this->assertSame(Order::PAYMENT_STATUS_REFUNDED, $fresh->payment_status);
        $this->assertEquals(50.0, (float) $fresh->refunded_amount);
    }

    public function test_charge_refunded_marks_partial_refund_when_amount_is_less_than_total(): void
    {
        $order = $this->order([
            'stripe_charge_id' => 'ch_partial',
            'total' => 100,
            'payment_status' => Order::PAYMENT_STATUS_PAID,
        ]);

        $response = $this->postSignedWebhook([
            'id' => 'evt_4',
            'type' => 'charge.refunded',
            'data' => ['object' => [
                'id' => 'ch_partial',
                'object' => 'charge',
                'amount_refunded' => 2500,
            ]],
        ]);

        $response->assertOk();
        $fresh = $order->fresh();
        $this->assertSame(Order::PAYMENT_STATUS_PARTIALLY_REFUNDED, $fresh->payment_status);
        $this->assertEquals(25.0, (float) $fresh->refunded_amount);
    }

    public function test_unknown_payment_intent_is_ignored_without_error(): void
    {
        $response = $this->postSignedWebhook([
            'id' => 'evt_5',
            'type' => 'payment_intent.succeeded',
            'data' => ['object' => [
                'id' => 'pi_does_not_exist',
                'object' => 'payment_intent',
            ]],
        ]);

        $response->assertOk();
    }

    public function test_unhandled_event_type_returns_ok(): void
    {
        $response = $this->postSignedWebhook([
            'id' => 'evt_6',
            'type' => 'customer.updated',
            'data' => ['object' => ['id' => 'cus_123']],
        ]);

        $response->assertOk();
    }
}
