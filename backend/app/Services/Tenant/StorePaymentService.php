<?php

declare(strict_types=1);

namespace App\Services\Tenant;

use App\Contracts\StorePaymentServiceInterface;
use App\Events\Tenant\OrderRefunded;
use App\Models\Tenant\Order;
use App\Models\Tenant\StorePaymentSettings;
use Illuminate\Support\Facades\Log;
use Stripe\PaymentIntent;
use Stripe\Refund;
use Stripe\Stripe;

class StorePaymentService implements StorePaymentServiceInterface
{
    private function setStripeKey(?StorePaymentSettings $settings = null): void
    {
        $key = $settings?->stripe_secret_key ?? config('services.stripe.secret');

        if (empty($key)) {
            throw new \RuntimeException('Stripe secret key is not configured for this store');
        }

        Stripe::setApiKey($key);
    }

    // ── PaymentIntent ─────────────────────────────────────────────────────────

    public function createPaymentIntent(Order $order, ?string $customerId = null): array
    {
        $settings = StorePaymentSettings::current();
        $this->setStripeKey($settings);

        try {
            $currency = $settings?->currency ?? 'eur';
            $captureMethod = $settings?->capture_method ?? 'automatic';
            $amountCents = (int) round((float) $order->total * 100);

            $params = [
                'amount' => $amountCents,
                'currency' => $currency,
                'capture_method' => $captureMethod,
                'metadata' => [
                    'order_id' => $order->id,
                    'tenant_id' => config('tenancy.tenant_id'),
                ],
            ];

            if ($customerId) {
                $params['customer'] = $customerId;
            }

            if ($settings?->statement_descriptor) {
                $params['statement_descriptor'] = substr($settings->statement_descriptor, 0, 22);
            }

            $intent = PaymentIntent::create($params);

            $order->update([
                'stripe_payment_intent_id' => $intent->id,
                'payment_status' => Order::PAYMENT_STATUS_PENDING,
            ]);

            return [
                'client_secret' => $intent->client_secret,
                'payment_intent_id' => $intent->id,
            ];
        } catch (\Throwable $e) {
            Log::error('StorePaymentService: createPaymentIntent failed', [
                'order_id' => $order->id,
                'error' => $e->getMessage(),
            ]);
            throw $e;
        }
    }

    // ── Capture ───────────────────────────────────────────────────────────────

    public function capturePayment(Order $order): Order
    {
        if (! $order->stripe_payment_intent_id) {
            throw new \RuntimeException("Order #{$order->id} has no PaymentIntent to capture");
        }

        $settings = StorePaymentSettings::current();
        $this->setStripeKey($settings);

        try {
            $intent = PaymentIntent::retrieve($order->stripe_payment_intent_id);
            $intent->capture();

            $order->update([
                'payment_status' => Order::PAYMENT_STATUS_PAID,
                'captured_at' => now(),
            ]);

            Log::info('StorePaymentService: payment captured', ['order_id' => $order->id]);

            return $order->fresh();
        } catch (\Throwable $e) {
            Log::error('StorePaymentService: capturePayment failed', [
                'order_id' => $order->id,
                'error' => $e->getMessage(),
            ]);
            throw $e;
        }
    }

    // ── Refund ────────────────────────────────────────────────────────────────

    public function refundOrder(Order $order, ?float $amount = null, ?string $reason = null): Order
    {
        if (! $order->stripe_payment_intent_id && ! $order->stripe_charge_id) {
            throw new \RuntimeException("Order #{$order->id} has no Stripe charge to refund");
        }

        $settings = StorePaymentSettings::current();
        $this->setStripeKey($settings);

        try {
            $totalCents = (int) round((float) $order->total * 100);
            $refundCents = $amount !== null
                ? (int) round($amount * 100)
                : $totalCents;

            $params = ['amount' => $refundCents];

            if ($order->stripe_charge_id) {
                $params['charge'] = $order->stripe_charge_id;
            } else {
                $params['payment_intent'] = $order->stripe_payment_intent_id;
            }

            if ($reason) {
                $params['reason'] = match ($reason) {
                    'duplicate' => 'duplicate',
                    'fraudulent' => 'fraudulent',
                    default => 'requested_by_customer',
                };
            }

            Refund::create($params);

            $refundedTotal = (float) $order->refunded_amount + ($refundCents / 100);
            $newStatus = $refundedTotal >= (float) $order->total
                ? Order::PAYMENT_STATUS_REFUNDED
                : Order::PAYMENT_STATUS_PARTIALLY_REFUNDED;

            $order->update([
                'payment_status' => $newStatus,
                'refunded_amount' => $refundedTotal,
                'refund_reason' => $reason,
                'refunded_at' => now(),
            ]);

            Log::info('StorePaymentService: order refunded', [
                'order_id' => $order->id,
                'amount_cents' => $refundCents,
                'status' => $newStatus,
            ]);

            $fresh = $order->fresh();
            event(new OrderRefunded($fresh, $refundCents / 100));

            return $fresh;
        } catch (\Throwable $e) {
            Log::error('StorePaymentService: refundOrder failed', [
                'order_id' => $order->id,
                'error' => $e->getMessage(),
            ]);
            throw $e;
        }
    }

    // ── Payment Methods ───────────────────────────────────────────────────────

    public function getPaymentMethods(StorePaymentSettings $settings): array
    {
        return $settings->payment_methods_enabled ?? ['card'];
    }
}
