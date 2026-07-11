<?php

declare(strict_types=1);

namespace Tests\Feature\Tenant;

use App\Models\Tenant\CartItem;
use App\Models\Tenant\CartSession;
use App\Models\Tenant\CheckoutSession;
use App\Models\Tenant\DiscountCode;
use App\Models\Tenant\Order;
use App\Models\Tenant\ShippingMethod;
use App\Services\Tenant\CheckoutService;
use Tests\Concerns\InteractsWithTenantRoutes;
use Tests\TenantTestCase;

class CheckoutApiTest extends TenantTestCase
{
    use InteractsWithTenantRoutes;

    protected function setUp(): void
    {
        parent::setUp();
        $this->bypassTenantDomainResolution();
    }

    /** @return array<string, mixed> */
    private function validAddress(): array
    {
        return [
            'first_name' => 'Mario',
            'last_name' => 'Rossi',
            'address_line_1' => 'Via Roma 1',
            'city' => 'Milano',
            'postal_code' => '20100',
            'country' => 'IT',
        ];
    }

    public function test_initiate_creates_checkout_session_with_computed_totals(): void
    {
        $cart = CartSession::factory()->create();
        CartItem::factory()->create(['cart_session_id' => $cart->id, 'quantity' => 2, 'unit_price' => 50]);
        $shipping = ShippingMethod::factory()->create(['price' => 5, 'is_active' => true]);

        $response = $this->postJson('/api/store/checkout', [
            'cart_session_id' => $cart->session_id,
            'shipping_method_id' => $shipping->id,
            'shipping_address' => $this->validAddress(),
        ]);

        $response->assertCreated();
        $this->assertEquals(100, $response->json('meta.subtotal'));
        $this->assertEquals(5, $response->json('meta.shipping'));
        $this->assertEquals(22, $response->json('meta.tax'));
        $this->assertEquals(127, $response->json('meta.total'));
        $this->assertDatabaseHas('checkout_sessions', [
            'cart_session_id' => $cart->id,
            'shipping_method_id' => $shipping->id,
        ]);
    }

    public function test_initiate_fails_for_empty_cart(): void
    {
        $cart = CartSession::factory()->create();
        $shipping = ShippingMethod::factory()->create();

        $response = $this->postJson('/api/store/checkout', [
            'cart_session_id' => $cart->session_id,
            'shipping_method_id' => $shipping->id,
            'shipping_address' => $this->validAddress(),
        ]);

        $response->assertStatus(422);
    }

    public function test_initiate_fails_for_unknown_cart_session(): void
    {
        $shipping = ShippingMethod::factory()->create();

        $response = $this->postJson('/api/store/checkout', [
            'cart_session_id' => 'does-not-exist',
            'shipping_method_id' => $shipping->id,
            'shipping_address' => $this->validAddress(),
        ]);

        $response->assertNotFound();
    }

    public function test_initiate_fails_for_inactive_shipping_method(): void
    {
        $cart = CartSession::factory()->create();
        CartItem::factory()->create(['cart_session_id' => $cart->id]);
        $shipping = ShippingMethod::factory()->inactive()->create();

        $response = $this->postJson('/api/store/checkout', [
            'cart_session_id' => $cart->session_id,
            'shipping_method_id' => $shipping->id,
            'shipping_address' => $this->validAddress(),
        ]);

        $response->assertStatus(422);
    }

    public function test_initiate_rejects_missing_required_address_fields(): void
    {
        $cart = CartSession::factory()->create();
        CartItem::factory()->create(['cart_session_id' => $cart->id]);
        $shipping = ShippingMethod::factory()->create();

        $response = $this->postJson('/api/store/checkout', [
            'cart_session_id' => $cart->session_id,
            'shipping_method_id' => $shipping->id,
            'shipping_address' => ['first_name' => 'Mario'],
        ]);

        $response->assertStatus(422);
        $response->assertJsonValidationErrors([
            'shipping_address.last_name',
            'shipping_address.address_line_1',
            'shipping_address.city',
            'shipping_address.postal_code',
            'shipping_address.country',
        ]);
    }

    public function test_show_returns_checkout_with_totals_including_discount(): void
    {
        $cart = CartSession::factory()->create();
        CartItem::factory()->create(['cart_session_id' => $cart->id, 'quantity' => 1, 'unit_price' => 100]);
        $shipping = ShippingMethod::factory()->create(['price' => 10]);
        $discount = DiscountCode::factory()->create(['type' => DiscountCode::TYPE_PERCENTAGE, 'value' => 10]);

        $checkout = app(CheckoutService::class)->initiate($cart, $this->validAddress(), $shipping->id);
        $checkout->update(['discount_code_id' => $discount->id]);

        $response = $this->getJson("/api/store/checkout/{$checkout->id}");

        $response->assertOk();
        $this->assertEquals(10, $response->json('meta.discount'));
    }

    /**
     * Regression test: the controller previously passed the raw Stringable
     * from $request->string('payment_intent_id') straight into
     * CheckoutService::confirmPayment(string $paymentIntentId), which has a
     * strict `string` type hint — PHP doesn't coerce objects to scalar type
     * hints, so every real confirm request threw a TypeError before it ever
     * reached application logic (payment succeeded on Stripe's side, but our
     * own endpoint 500'd). Uses the already-completed idempotent path so it
     * exercises the full HTTP → FormRequest → controller → service chain
     * without a live Stripe call.
     */
    public function test_confirm_endpoint_accepts_payment_intent_id_for_already_completed_checkout(): void
    {
        $checkout = CheckoutSession::factory()->create([
            'status' => CheckoutSession::STATUS_COMPLETED,
            'stripe_payment_intent_id' => 'pi_already_done',
        ]);
        $order = Order::factory()->paid()->create([
            'metadata' => ['checkout_session_id' => $checkout->id],
        ]);

        $response = $this->postJson("/api/store/checkout/{$checkout->id}/confirm", [
            'payment_intent_id' => 'pi_already_done',
        ]);

        $response->assertOk();
        $this->assertEquals($order->id, $response->json('data.id'));
    }
}
