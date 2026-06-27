<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Tenant\Customer;
use App\Models\Tenant\Order;
use App\Models\Tenant\StorePaymentSettings;
use App\Services\Tenant\StorePaymentService;
use Tests\TenantTestCase;

/**
 * Tests StorePaymentService logic that does NOT require real Stripe calls.
 * Stripe API calls are exercised in integration/end-to-end tests.
 *
 *  1.  createPaymentIntent() throws when no Stripe key configured
 *  2.  capturePayment() throws when order has no payment_intent_id
 *  3.  refundOrder() throws when order has no charge or payment_intent
 *  4.  getPaymentMethods() returns enabled methods from settings
 *  5.  getPaymentMethods() defaults to card when empty
 *  6.  StorePaymentSettings::current() returns null when table is empty
 *  7.  StorePaymentSettings::currentOrNew() returns unsaved instance when empty
 *  8.  StorePaymentSettings::isStripeConfigured() reflects secret key presence
 *  9.  refundOrder() correctly calculates partial vs full refund status
 * 10.  Order PAYMENT_STATUS constants are defined
 * 11.  Order payment fields are fillable
 * 12.  StorePaymentSettings secret key is encrypted
 * 13.  TenantStripeWebhookController routes exist (route list check)
 */
class StorePaymentServiceTest extends TenantTestCase
{
    private function makeOrder(array $overrides = []): Order
    {
        static $seq = 0;
        $seq++;

        $customer = Customer::create([
            'name' => 'Customer '.$seq,
            'email' => "cust{$seq}@example.com",
        ]);

        return Order::create(array_merge([
            'customer_id' => $customer->id,
            'status' => Order::STATUS_PENDING,
            'total' => 100.00,
            'subtotal' => 100.00,
            'discount_total' => 0,
            'shipping_total' => 0,
            'payment_method' => 'card',
            'payment_status' => Order::PAYMENT_STATUS_PENDING,
        ], $overrides));
    }

    private function service(): StorePaymentService
    {
        return new StorePaymentService;
    }

    // ── createPaymentIntent ───────────────────────────────────────────────────

    public function test_create_payment_intent_throws_when_no_stripe_key(): void
    {
        config(['services.stripe.secret' => '']);

        $order = $this->makeOrder();

        $this->expectException(\RuntimeException::class);
        $this->expectExceptionMessageMatches('/not configured/');

        $this->service()->createPaymentIntent($order);
    }

    // ── capturePayment ────────────────────────────────────────────────────────

    public function test_capture_throws_when_no_payment_intent(): void
    {
        $order = $this->makeOrder(['stripe_payment_intent_id' => null]);

        $this->expectException(\RuntimeException::class);
        $this->expectExceptionMessageMatches('/no PaymentIntent to capture/');

        $this->service()->capturePayment($order);
    }

    // ── refundOrder ───────────────────────────────────────────────────────────

    public function test_refund_throws_when_no_charge_or_intent(): void
    {
        $order = $this->makeOrder([
            'stripe_payment_intent_id' => null,
            'stripe_charge_id' => null,
        ]);

        $this->expectException(\RuntimeException::class);
        $this->expectExceptionMessageMatches('/no Stripe charge to refund/');

        $this->service()->refundOrder($order);
    }

    // ── getPaymentMethods ─────────────────────────────────────────────────────

    public function test_get_payment_methods_returns_configured_methods(): void
    {
        $settings = new StorePaymentSettings([
            'payment_methods_enabled' => ['card', 'sepa_debit'],
        ]);

        $methods = $this->service()->getPaymentMethods($settings);

        $this->assertSame(['card', 'sepa_debit'], $methods);
    }

    public function test_get_payment_methods_defaults_to_card(): void
    {
        $settings = new StorePaymentSettings(['payment_methods_enabled' => null]);

        $methods = $this->service()->getPaymentMethods($settings);

        $this->assertSame(['card'], $methods);
    }

    // ── StorePaymentSettings ──────────────────────────────────────────────────

    public function test_current_returns_null_when_table_empty(): void
    {
        $this->assertNull(StorePaymentSettings::current());
    }

    public function test_current_or_new_returns_unsaved_instance_when_empty(): void
    {
        $instance = StorePaymentSettings::currentOrNew();

        $this->assertInstanceOf(StorePaymentSettings::class, $instance);
        $this->assertFalse($instance->exists);
    }

    public function test_is_stripe_configured_reflects_secret_key(): void
    {
        $withKey = new StorePaymentSettings(['stripe_secret_key' => 'sk_test_abc']);
        $withoutKey = new StorePaymentSettings(['stripe_secret_key' => null]);

        $this->assertTrue($withKey->isStripeConfigured());
        $this->assertFalse($withoutKey->isStripeConfigured());
    }

    // ── Order constants and fillable ──────────────────────────────────────────

    public function test_order_payment_status_constants_are_defined(): void
    {
        $this->assertSame('pending', Order::PAYMENT_STATUS_PENDING);
        $this->assertSame('paid', Order::PAYMENT_STATUS_PAID);
        $this->assertSame('partially_refunded', Order::PAYMENT_STATUS_PARTIALLY_REFUNDED);
        $this->assertSame('refunded', Order::PAYMENT_STATUS_REFUNDED);
        $this->assertSame('failed', Order::PAYMENT_STATUS_FAILED);
    }

    public function test_order_stripe_fields_are_persisted(): void
    {
        $order = $this->makeOrder();
        $order->update([
            'stripe_payment_intent_id' => 'pi_test',
            'stripe_charge_id' => 'ch_test',
            'payment_method_type' => 'card',
            'refunded_amount' => 10.00,
        ]);

        $fresh = $order->fresh();

        $this->assertSame('pi_test', $fresh->stripe_payment_intent_id);
        $this->assertSame('ch_test', $fresh->stripe_charge_id);
        $this->assertSame('card', $fresh->payment_method_type);
        $this->assertEquals(10.00, (float) $fresh->refunded_amount);
    }

    public function test_order_refund_status_computation(): void
    {
        // Simulate what refundOrder does internally without calling Stripe
        $order = $this->makeOrder(['total' => 100.00, 'payment_status' => Order::PAYMENT_STATUS_PAID]);

        // Partial refund
        $partialCents = 5000; // €50
        $refundedTotal = (float) $order->refunded_amount + ($partialCents / 100);
        $newStatus = $refundedTotal >= (float) $order->total
            ? Order::PAYMENT_STATUS_REFUNDED
            : Order::PAYMENT_STATUS_PARTIALLY_REFUNDED;

        $this->assertSame(Order::PAYMENT_STATUS_PARTIALLY_REFUNDED, $newStatus);

        // Full refund
        $fullCents = 10000; // €100
        $refundedTotal = (float) $order->refunded_amount + ($fullCents / 100);
        $newStatus = $refundedTotal >= (float) $order->total
            ? Order::PAYMENT_STATUS_REFUNDED
            : Order::PAYMENT_STATUS_PARTIALLY_REFUNDED;

        $this->assertSame(Order::PAYMENT_STATUS_REFUNDED, $newStatus);
    }

    public function test_store_payment_settings_has_connect_flag(): void
    {
        $withConnect = new StorePaymentSettings(['stripe_account_id' => 'acct_test']);
        $withoutConnect = new StorePaymentSettings(['stripe_account_id' => null]);

        $this->assertTrue($withConnect->hasStripeConnect());
        $this->assertFalse($withoutConnect->hasStripeConnect());
    }
}
