<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Jobs\ProcessStripeWebhookJob;
use App\Models\Central\BillingEvent;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Illuminate\Support\Facades\Log;
use Stripe\Exception\SignatureVerificationException;
use Stripe\Webhook;

class StripeWebhookController extends Controller
{
    /**
     * Riceve webhook da Stripe.
     *
     * Regole:
     * - Valida la firma PRIMA di fare qualsiasi cosa
     * - Scrive il BillingEvent in modo idempotente (ON CONFLICT stripe_event_id → ignore)
     * - Se già processato → 200 immediato
     * - Dispatcha il job asincrono per il processing reale
     * - Ritorna sempre 200 a Stripe (errori finiscono nel job/log, mai bloccano la response)
     */
    public function handle(Request $request): Response
    {
        // 1. Valida firma Stripe
        $payload   = $request->getContent();
        $sigHeader = $request->header('Stripe-Signature', '');
        $secret    = config('services.stripe.webhook_secret');

        try {
            $event = Webhook::constructEvent($payload, $sigHeader, $secret);
        } catch (SignatureVerificationException $e) {
            Log::warning('Stripe webhook invalid signature', ['error' => $e->getMessage()]);
            return response('Invalid signature', 400);
        } catch (\Throwable $e) {
            Log::error('Stripe webhook parse error', ['error' => $e->getMessage()]);
            return response('Webhook error', 400);
        }

        // 2. Scrivi BillingEvent in modo idempotente
        // insertOrIgnore: se stripe_event_id già esiste, non fa nulla e non lancia eccezione
        $inserted = BillingEvent::insertOrIgnore([
            'stripe_event_id' => $event->id,
            'event_type'      => $event->type,
            'payload'         => json_encode($event->toArray()),
            'processed_at'    => null,
            'created_at'      => now(),
        ]);

        if (!$inserted) {
            // Evento già registrato — controlla se già processato
            $existing = BillingEvent::where('stripe_event_id', $event->id)->first();
            if ($existing?->isProcessed()) {
                return response('Already processed', 200);
            }
            // Non ancora processato (es. job fallito): ri-dispatcha
            if ($existing) {
                ProcessStripeWebhookJob::dispatch($existing->id);
            }
            return response('OK', 200);
        }

        // 3. Carica il record appena inserito e dispatcha il job
        $billingEvent = BillingEvent::where('stripe_event_id', $event->id)->firstOrFail();
        ProcessStripeWebhookJob::dispatch($billingEvent->id);

        return response('OK', 200);
    }
}
