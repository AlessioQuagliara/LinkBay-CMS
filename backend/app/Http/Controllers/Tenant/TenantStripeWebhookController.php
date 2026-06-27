<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tenant;

use App\Http\Controllers\Controller;
use App\Models\Tenant\Order;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Illuminate\Support\Facades\Log;
use Stripe\Exception\SignatureVerificationException;
use Stripe\Webhook;

class TenantStripeWebhookController extends Controller
{
    /**
     * Receives Stripe webhooks scoped to this tenant's store.
     *
     * Uses the store's own webhook secret (if configured) or falls back
     * to the platform secret. Always returns 200 to Stripe — errors go to logs.
     */
    public function handle(Request $request): Response
    {
        $payload = $request->getContent();
        $sigHeader = $request->header('Stripe-Signature', '');

        // Prefer store-level secret, fall back to platform secret
        $secret = config('services.stripe.tenant_webhook_secret')
            ?? config('services.stripe.webhook_secret');

        try {
            $event = Webhook::constructEvent($payload, $sigHeader, $secret);
        } catch (SignatureVerificationException $e) {
            Log::warning('TenantStripeWebhook: invalid signature', ['error' => $e->getMessage()]);

            return response('Invalid signature', 400);
        } catch (\Throwable $e) {
            Log::error('TenantStripeWebhook: parse error', ['error' => $e->getMessage()]);

            return response('Webhook error', 400);
        }

        $obj = $event->data->object->toArray();
        $type = $event->type;

        try {
            match ($type) {
                'payment_intent.succeeded' => $this->onPaymentIntentSucceeded($obj),
                'payment_intent.payment_failed' => $this->onPaymentIntentFailed($obj),
                'charge.refunded' => $this->onChargeRefunded($obj),
                default => null,
            };
        } catch (\Throwable $e) {
            Log::error('TenantStripeWebhook: handler failed', [
                'event_type' => $type,
                'event_id' => $event->id,
                'error' => $e->getMessage(),
            ]);
        }

        return response('OK', 200);
    }

    // ── Handlers ──────────────────────────────────────────────────────────────

    private function onPaymentIntentSucceeded(array $obj): void
    {
        $piId = $obj['id'] ?? null;
        if (! $piId) {
            return;
        }

        $order = Order::where('stripe_payment_intent_id', $piId)->first();
        if (! $order) {
            return;
        }

        $chargeId = $obj['latest_charge'] ?? null;

        $order->update([
            'payment_status' => Order::PAYMENT_STATUS_PAID,
            'stripe_charge_id' => $chargeId,
            'captured_at' => now(),
        ]);

        Log::info('TenantStripeWebhook: order paid', ['order_id' => $order->id, 'pi' => $piId]);
    }

    private function onPaymentIntentFailed(array $obj): void
    {
        $piId = $obj['id'] ?? null;
        if (! $piId) {
            return;
        }

        $order = Order::where('stripe_payment_intent_id', $piId)->first();
        if (! $order) {
            return;
        }

        $order->update(['payment_status' => Order::PAYMENT_STATUS_FAILED]);

        Log::warning('TenantStripeWebhook: payment failed', ['order_id' => $order->id, 'pi' => $piId]);
    }

    private function onChargeRefunded(array $obj): void
    {
        $chargeId = $obj['id'] ?? null;
        if (! $chargeId) {
            return;
        }

        $order = Order::where('stripe_charge_id', $chargeId)->first();
        if (! $order) {
            return;
        }

        $refundedCents = (int) ($obj['amount_refunded'] ?? 0);
        $totalCents = (int) round((float) $order->total * 100);

        $newStatus = $refundedCents >= $totalCents
            ? Order::PAYMENT_STATUS_REFUNDED
            : Order::PAYMENT_STATUS_PARTIALLY_REFUNDED;

        $order->update([
            'payment_status' => $newStatus,
            'refunded_amount' => $refundedCents / 100,
            'refunded_at' => now(),
        ]);

        Log::info('TenantStripeWebhook: charge refunded', [
            'order_id' => $order->id,
            'refunded_cents' => $refundedCents,
            'status' => $newStatus,
        ]);
    }
}
