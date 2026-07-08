<?php

declare(strict_types=1);

namespace Tests\Feature\Tenant;

use App\Models\Tenant\CartItem;
use App\Models\Tenant\CartSession;
use App\Models\Tenant\CheckoutSession;
use App\Models\Tenant\DiscountCode;
use App\Models\Tenant\Order;
use App\Models\Tenant\Product;
use App\Services\Tenant\CheckoutService;
use Illuminate\Database\Eloquent\ModelNotFoundException;
use RuntimeException;
use Tests\TenantTestCase;

/**
 * Exercises CheckoutService::convertToOrder() and confirmPayment() directly,
 * without going through Stripe's API (createPaymentIntent/confirmPayment's
 * "succeeded" branch require a live Stripe call — see StorePaymentServiceTest
 * for why the existing suite avoids that too). A CheckoutSession is put
 * directly into STATUS_PROCESSING to simulate a Stripe-confirmed payment.
 */
class CheckoutOrderConversionTest extends TenantTestCase
{
    private function service(): CheckoutService
    {
        return app(CheckoutService::class);
    }

    private function processingCheckout(array $overrides = []): CheckoutSession
    {
        $cart = CartSession::factory()->create();
        $product = Product::factory()->create(['price' => 25]);
        CartItem::factory()->create(['cart_session_id' => $cart->id, 'product_id' => $product->id, 'quantity' => 2, 'unit_price' => 25]);

        return CheckoutSession::factory()->create(array_merge([
            'cart_session_id' => $cart->id,
            'status' => CheckoutSession::STATUS_PROCESSING,
            'subtotal' => 50,
            'total' => 50,
        ], $overrides));
    }

    public function test_convert_to_order_creates_order_with_items_and_completes_checkout(): void
    {
        $checkout = $this->processingCheckout();

        $order = $this->service()->convertToOrder($checkout);

        $this->assertSame(Order::STATUS_CONFIRMED, $order->status);
        $this->assertSame(1, $order->items()->count());
        $this->assertSame(CheckoutSession::STATUS_COMPLETED, $checkout->fresh()->status);
        $this->assertNotNull($checkout->fresh()->completed_at);
    }

    public function test_convert_to_order_increments_discount_used_count(): void
    {
        $discount = DiscountCode::factory()->create(['used_count' => 0]);
        $checkout = $this->processingCheckout(['discount_code_id' => $discount->id]);

        $this->service()->convertToOrder($checkout);

        $this->assertSame(1, $discount->fresh()->used_count);
    }

    public function test_convert_to_order_throws_when_checkout_is_not_processing(): void
    {
        $checkout = $this->processingCheckout(['status' => CheckoutSession::STATUS_PENDING]);

        $this->expectException(RuntimeException::class);

        $this->service()->convertToOrder($checkout);
    }

    public function test_convert_to_order_is_idempotent_for_already_completed_checkout(): void
    {
        $checkout = $this->processingCheckout();

        $firstOrder = $this->service()->convertToOrder($checkout);
        $secondOrder = $this->service()->convertToOrder($checkout->fresh());

        $this->assertSame($firstOrder->id, $secondOrder->id);
        $this->assertSame(1, Order::count());
    }

    public function test_confirm_payment_throws_for_unknown_payment_intent(): void
    {
        $this->expectException(ModelNotFoundException::class);

        $this->service()->confirmPayment('pi_does_not_exist');
    }

    public function test_confirm_payment_is_idempotent_for_already_completed_checkout(): void
    {
        $checkout = CheckoutSession::factory()->create([
            'status' => CheckoutSession::STATUS_COMPLETED,
            'stripe_payment_intent_id' => 'pi_already_done',
        ]);

        $result = $this->service()->confirmPayment('pi_already_done');

        $this->assertSame($checkout->id, $result->id);
        $this->assertSame(CheckoutSession::STATUS_COMPLETED, $result->status);
    }
}
