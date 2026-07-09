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
use Illuminate\Database\Eloquent\ModelNotFoundException;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;
use RuntimeException;
use Stripe\StripeClient;

class CheckoutService
{
    public function initiate(CartSession $cart, array $shippingAddress, int $shippingMethodId): CheckoutSession
    {
        $shippingMethod = ShippingMethod::where('id', $shippingMethodId)
            ->where('is_active', true)
            ->first();

        if (! $shippingMethod) {
            throw new ModelNotFoundException('Il metodo di spedizione selezionato non è più disponibile.');
        }

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

    /**
     * Reusable/still-pending PaymentIntent statuses — safe to hand the same
     * client_secret back out again instead of creating a new intent.
     */
    private const REUSABLE_INTENT_STATUSES = [
        'requires_payment_method',
        'requires_confirmation',
        'requires_action',
        'processing',
    ];

    /**
     * Creates (or reuses) the Stripe PaymentIntent for a checkout.
     *
     * Idempotency has two layers, because this is called from the "proceed to
     * payment" step and can be retried by a double-click, a page reload before
     * the first response arrives, or a network retry:
     *  1. Application-level: if the checkout already has a PaymentIntent in a
     *     reusable state, its client_secret is returned unchanged instead of
     *     creating a new intent (which would previously overwrite
     *     stripe_payment_intent_id and orphan the first intent in Stripe).
     *  2. Stripe-level: the create call itself carries a deterministic
     *     idempotency key derived from the checkout id, so even if two
     *     requests race past check #1 (TOCTOU — no DB lock here, unlike
     *     convertToOrder), Stripe's own API deduplicates the create and
     *     returns the same PaymentIntent for both.
     */
    public function createPaymentIntent(CheckoutSession $checkout): string
    {
        $secret = config('services.stripe.secret');

        if (empty($secret)) {
            throw new RuntimeException('Il pagamento online non è configurato per questo store.');
        }

        try {
            $stripe = new StripeClient($secret);

            if ($checkout->stripe_payment_intent_id) {
                $existing = $stripe->paymentIntents->retrieve($checkout->stripe_payment_intent_id);
                if (in_array($existing->status, self::REUSABLE_INTENT_STATUSES, true)) {
                    return $existing->client_secret;
                }
            }

            $intent = $stripe->paymentIntents->create([
                'amount' => (int) round((float) $checkout->total * 100),
                'currency' => 'eur',
                'metadata' => [
                    'checkout_session_id' => $checkout->id,
                ],
            ], [
                'idempotency_key' => 'checkout-'.$checkout->id.'-intent',
            ]);

            $checkout->update([
                'stripe_payment_intent_id' => $intent->id,
                'stripe_payment_status' => $intent->status,
            ]);

            return $intent->client_secret;
        } catch (RuntimeException $e) {
            throw $e;
        } catch (\Throwable $e) {
            Log::error('CheckoutService: createPaymentIntent failed', [
                'checkout_id' => $checkout->id,
                'error' => $e->getMessage(),
            ]);
            throw new RuntimeException('Impossibile inizializzare il pagamento. Riprova tra qualche istante.', previous: $e);
        }
    }

    public function confirmPayment(string $paymentIntentId): CheckoutSession
    {
        $checkout = CheckoutSession::where('stripe_payment_intent_id', $paymentIntentId)->first();

        if (! $checkout) {
            throw new ModelNotFoundException('Sessione di pagamento non trovata. Riprova il checkout.');
        }

        // Idempotency: a retried confirm call must not downgrade an already-completed checkout.
        if ($checkout->status === CheckoutSession::STATUS_COMPLETED) {
            return $checkout;
        }

        try {
            $stripe = new StripeClient(config('services.stripe.secret'));
            $intent = $stripe->paymentIntents->retrieve($paymentIntentId);
        } catch (\Throwable $e) {
            Log::error('CheckoutService: confirmPayment failed to retrieve intent', [
                'checkout_id' => $checkout->id,
                'error' => $e->getMessage(),
            ]);
            throw new RuntimeException('Impossibile verificare lo stato del pagamento. Riprova tra qualche istante.', previous: $e);
        }

        $checkout->update([
            'stripe_payment_status' => $intent->status,
            'status' => $intent->status === 'succeeded'
                ? CheckoutSession::STATUS_PROCESSING
                : CheckoutSession::STATUS_PENDING,
        ]);

        if ($intent->status !== 'succeeded') {
            throw new RuntimeException('Il pagamento non risulta completato (stato: '.$intent->status.').');
        }

        return $checkout->fresh();
    }

    /**
     * Looks up the order produced by a completed checkout session, if any.
     * Public (unauthenticated) storefront routes use this to show the guest
     * checkout success page without requiring a customer session — see
     * CheckoutController::order().
     */
    public function findOrderFor(CheckoutSession $checkout): ?Order
    {
        return Order::where('metadata->checkout_session_id', $checkout->id)->first();
    }

    /**
     * Creates the Order for a confirmed checkout.
     *
     * Concurrency: two near-simultaneous confirm() calls for the same checkout
     * (double-click, retried request after a slow response) both used to be able
     * to pass the "not completed yet" check before either committed, creating two
     * orders for one checkout. Everything now runs inside a transaction that
     * re-fetches the checkout row with lockForUpdate() first — the second caller
     * blocks until the first transaction commits, then sees STATUS_COMPLETED and
     * returns the existing order via findOrderFor() instead of creating another.
     * (SQLite, used in tests, has no real row-level locking — lockForUpdate() is
     * a no-op there. The behavior this protects against can only be observed
     * under a real concurrent load against Postgres.)
     */
    public function convertToOrder(CheckoutSession $checkout): Order
    {
        return DB::transaction(function () use ($checkout) {
            $locked = CheckoutSession::whereKey($checkout->id)->lockForUpdate()->firstOrFail();

            if ($locked->status === CheckoutSession::STATUS_COMPLETED) {
                $existing = $this->findOrderFor($locked);
                if ($existing) {
                    return $existing;
                }
            }

            if ($locked->status !== CheckoutSession::STATUS_PROCESSING) {
                throw new RuntimeException('Il pagamento non risulta completato: impossibile creare l\'ordine.');
            }

            $locked->loadMissing('cartSession.cartItems.product');

            $order = Order::create([
                'customer_id' => $locked->customer_id,
                'status' => Order::STATUS_CONFIRMED,
                'subtotal' => $locked->subtotal,
                'shipping_total' => $locked->shipping_amount,
                'discount_total' => $locked->discount_amount,
                'total' => $locked->total,
                'shipping_method_id' => $locked->shipping_method_id,
                'discount_code_id' => $locked->discount_code_id,
                'shipping_address' => $locked->shipping_address,
                'billing_address' => $locked->billing_address ?? $locked->shipping_address,
                'payment_method' => 'stripe',
                'payment_status' => 'paid',
                // Required for TenantStripeWebhookController to find this order later
                // (payment_intent.succeeded/failed, charge.refunded all look it up by
                // this column) — without it those webhook handlers silently no-op.
                'stripe_payment_intent_id' => $locked->stripe_payment_intent_id,
                'metadata' => ['checkout_session_id' => $locked->id],
            ]);

            foreach ($locked->cartSession->cartItems as $cartItem) {
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

            if ($locked->discount_code_id) {
                DiscountCode::find($locked->discount_code_id)?->increment('used_count');
            }

            $locked->update([
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
