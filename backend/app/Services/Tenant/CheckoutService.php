<?php

declare(strict_types=1);

namespace App\Services\Tenant;

use App\Events\Tenant\OrderPlaced;
use App\Models\Tenant\CartItem;
use App\Models\Tenant\CartSession;
use App\Models\Tenant\CheckoutSession;
use App\Models\Tenant\DiscountCode;
use App\Models\Tenant\Order;
use App\Models\Tenant\OrderItem;
use App\Models\Tenant\ShippingMethod;
use Illuminate\Support\Facades\DB;
use RuntimeException;
use Stripe\StripeClient;

class CheckoutService
{
    public function initiate(CartSession $cart, array $shippingAddress, int $shippingMethodId): CheckoutSession
    {
        $shippingMethod = ShippingMethod::findOrFail($shippingMethodId);

        $totals = $this->computeTotals($cart, $shippingMethod, null);

        return CheckoutSession::create([
            'cart_session_id' => $cart->id,
            'customer_id' => $cart->customer_id,
            'status' => CheckoutSession::STATUS_PENDING,
            'shipping_address' => $shippingAddress,
            'shipping_method_id' => $shippingMethodId,
            'subtotal' => $totals['subtotal'],
            'shipping_amount' => $totals['shipping'],
            'discount_amount' => $totals['discount'],
            'tax_amount' => $totals['tax'],
            'total' => $totals['total'],
        ]);
    }

    public function createPaymentIntent(CheckoutSession $checkout): string
    {
        $stripe = new StripeClient(config('services.stripe.secret'));

        $intent = $stripe->paymentIntents->create([
            'amount' => (int) round((float) $checkout->total * 100),
            'currency' => 'eur',
            'metadata' => [
                'checkout_session_id' => $checkout->id,
            ],
        ]);

        $checkout->update([
            'stripe_payment_intent_id' => $intent->id,
            'stripe_payment_status' => $intent->status,
        ]);

        return $intent->client_secret;
    }

    public function confirmPayment(string $paymentIntentId): CheckoutSession
    {
        $stripe = new StripeClient(config('services.stripe.secret'));

        $intent = $stripe->paymentIntents->retrieve($paymentIntentId);

        $checkout = CheckoutSession::where('stripe_payment_intent_id', $paymentIntentId)->firstOrFail();

        $checkout->update([
            'stripe_payment_status' => $intent->status,
            'status' => $intent->status === 'succeeded'
                ? CheckoutSession::STATUS_PROCESSING
                : CheckoutSession::STATUS_PENDING,
        ]);

        return $checkout->fresh();
    }

    public function convertToOrder(CheckoutSession $checkout): Order
    {
        if ($checkout->status !== CheckoutSession::STATUS_PROCESSING) {
            throw new RuntimeException('Checkout must be in processing state to convert to order.');
        }

        return DB::transaction(function () use ($checkout) {
            $checkout->loadMissing('cartSession.cartItems.product');

            $order = Order::create([
                'customer_id' => $checkout->customer_id,
                'status' => Order::STATUS_CONFIRMED,
                'subtotal' => $checkout->subtotal,
                'shipping_total' => $checkout->shipping_amount,
                'discount_total' => $checkout->discount_amount,
                'total' => $checkout->total,
                'shipping_method_id' => $checkout->shipping_method_id,
                'discount_code_id' => $checkout->discount_code_id,
                'shipping_address' => $checkout->shipping_address,
                'billing_address' => $checkout->billing_address ?? $checkout->shipping_address,
                'payment_method' => 'stripe',
                'payment_status' => 'paid',
                'metadata' => ['checkout_session_id' => $checkout->id],
            ]);

            foreach ($checkout->cartSession->cartItems as $cartItem) {
                OrderItem::create([
                    'order_id' => $order->id,
                    'product_id' => $cartItem->product_id,
                    'name' => $cartItem->product->name,
                    'sku' => $cartItem->product->sku,
                    'quantity' => $cartItem->quantity,
                    'price' => $cartItem->unit_price,
                    'total' => (float) $cartItem->unit_price * $cartItem->quantity,
                ]);
            }

            if ($checkout->discount_code_id) {
                DiscountCode::find($checkout->discount_code_id)?->increment('used_count');
            }

            $checkout->update([
                'status' => CheckoutSession::STATUS_COMPLETED,
                'completed_at' => now(),
            ]);

            event(new OrderPlaced($order));

            return $order;
        });
    }

    /**
     * @return array{subtotal: float, discount: float, shipping: float, tax: float, total: float}
     */
    public function calculateTotals(CheckoutSession $checkout): array
    {
        $checkout->loadMissing('cartSession', 'shippingMethod', 'discountCode');

        return $this->computeTotals(
            $checkout->cartSession,
            $checkout->shippingMethod,
            $checkout->discountCode
        );
    }

    /**
     * @return array{subtotal: float, discount: float, shipping: float, tax: float, total: float}
     */
    private function computeTotals(CartSession $cart, ?ShippingMethod $shippingMethod, ?DiscountCode $discountCode): array
    {
        $cart->loadMissing('cartItems');

        $subtotal = $cart->cartItems->sum(fn (CartItem $item) => (float) $item->unit_price * $item->quantity);

        $shipping = $shippingMethod ? (float) $shippingMethod->price : 0.0;

        $discount = 0.0;
        if ($discountCode && $discountCode->isValid()) {
            $discount = match ($discountCode->type) {
                DiscountCode::TYPE_PERCENTAGE => round($subtotal * ((float) $discountCode->value / 100), 2),
                DiscountCode::TYPE_FIXED => min((float) $discountCode->value, $subtotal),
                DiscountCode::TYPE_FREE_SHIPPING => $shipping,
                default => 0.0,
            };
        }

        $taxable = $subtotal - $discount;
        $tax = round($taxable * 0.22, 2); // IVA italiana default
        $total = round($subtotal + $shipping - $discount + $tax, 2);

        return [
            'subtotal' => round($subtotal, 2),
            'discount' => round($discount, 2),
            'shipping' => round($shipping, 2),
            'tax' => $tax,
            'total' => $total,
        ];
    }
}
