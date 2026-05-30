<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Central\Agency;
use App\Models\Central\AgencySubscription;
use App\Models\Central\Plan;
use Carbon\Carbon;
use Illuminate\Support\Facades\Log;
use Stripe\Invoice;
use Stripe\Subscription;

class AgencySubscriptionService
{
    /**
     * Cambia piano di un'agency con subscription Stripe attiva.
     *
     * Aggiorna il subscription item esistente — NON crea una seconda subscription.
     * Fonte di verità: Stripe. Il DB locale viene sincronizzato dal risultato API.
     *
     * @throws \RuntimeException se non esiste una subscription aggiornabile
     */
    public function changeAgencyPlan(Agency $agency, Plan $newPlan): AgencySubscription
    {
        \Stripe\Stripe::setApiKey(config('services.stripe.secret'));

        $localSub = AgencySubscription::where('agency_id', $agency->id)
            ->whereNotNull('stripe_subscription_id')
            ->first();

        if (!$localSub?->stripe_subscription_id) {
            throw new \RuntimeException(
                "Agency #{$agency->id}: no Stripe subscription found — use checkout for new subscription"
            );
        }

        // Recupera la subscription da Stripe (fonte di verità)
        $stripeSub = \Stripe\Subscription::retrieve([
            'id'     => $localSub->stripe_subscription_id,
            'expand' => ['items'],
        ]);

        if (!in_array($stripeSub->status, ['active', 'trialing', 'past_due'], true)) {
            throw new \RuntimeException(
                "Subscription {$localSub->stripe_subscription_id} cannot be updated (status: {$stripeSub->status})"
            );
        }

        $itemId = $stripeSub->items->data[0]->id ?? null;
        if (!$itemId) {
            throw new \RuntimeException(
                "No subscription item found on {$localSub->stripe_subscription_id}"
            );
        }

        // Aggiorna il price sull'item esistente — zero nuove subscription create
        $updated = \Stripe\Subscription::update($localSub->stripe_subscription_id, [
            'items' => [
                [
                    'id'    => $itemId,
                    'price' => $newPlan->stripe_price_id,
                ],
            ],
            'proration_behavior' => 'create_prorations',
        ]);

        Log::info('AgencySubscriptionService: plan changed via subscription update', [
            'agency_id'       => $agency->id,
            'subscription_id' => $localSub->stripe_subscription_id,
            'old_plan_id'     => $agency->plan_id,
            'new_plan_id'     => $newPlan->id,
            'new_price_id'    => $newPlan->stripe_price_id,
        ]);

        return $this->syncFromStripe($updated);
    }

    /**
     * Crea o aggiorna AgencySubscription da un oggetto Stripe Subscription.
     * Chiamato da webhook: customer.subscription.created / updated.
     * Chiamato internamente da changeAgencyPlan() dopo l'update Stripe.
     *
     * Se arriva una subscription con ID diverso da quello tracked, logga l'anomalia
     * e aggiorna comunque (la vecchia sarà o sarà cancellata da Stripe).
     */
    public function syncFromStripe(Subscription $stripeSub): AgencySubscription
    {
        $agency = Agency::where('stripe_customer_id', $stripeSub->customer)->first();

        if (!$agency) {
            throw new \RuntimeException("Agency not found for Stripe customer {$stripeSub->customer}");
        }

        $priceId = $stripeSub->items->data[0]->price->id ?? null;
        $plan    = $priceId ? Plan::where('stripe_price_id', $priceId)->first() : null;

        // Anomaly detection: se c'è già una sub trackkata con ID diverso, logga
        $existing = AgencySubscription::where('agency_id', $agency->id)->first();
        if (
            $existing
            && $existing->stripe_subscription_id
            && $existing->stripe_subscription_id !== $stripeSub->id
            && in_array($existing->status, ['active', 'trialing'], true)
        ) {
            Log::warning('AgencySubscriptionService: new subscription while another is tracked — possible duplicate', [
                'agency_id'       => $agency->id,
                'tracked_sub'     => $existing->stripe_subscription_id,
                'incoming_sub'    => $stripeSub->id,
                'incoming_status' => $stripeSub->status,
            ]);
        }

        $sub = AgencySubscription::updateOrCreate(
            ['agency_id' => $agency->id],
            [
                'plan_id'                => $plan?->id ?? $agency->plan_id,
                'stripe_subscription_id' => $stripeSub->id,
                'stripe_customer_id'     => $stripeSub->customer,
                'status'                 => $stripeSub->status,
                'billing_type'           => $agency->billing_type,
                'current_period_start'   => $stripeSub->current_period_start
                    ? Carbon::createFromTimestamp($stripeSub->current_period_start)
                    : null,
                'current_period_end'     => $stripeSub->current_period_end
                    ? Carbon::createFromTimestamp($stripeSub->current_period_end)
                    : null,
                'trial_ends_at'          => $stripeSub->trial_end
                    ? Carbon::createFromTimestamp($stripeSub->trial_end)
                    : null,
                'cancelled_at'           => $stripeSub->canceled_at
                    ? Carbon::createFromTimestamp($stripeSub->canceled_at)
                    : null,
            ]
        );

        if ($plan && $agency->plan_id !== $plan->id) {
            $agency->update(['plan_id' => $plan->id]);
        }

        return $sub;
    }

    /**
     * Chiamato da webhook: customer.subscription.deleted.
     *
     * Sospende l'agency SOLO se la subscription cancellata è quella attualmente trackata.
     * Se è una subscription orfana/vecchia (es. doppio checkout per errore passato),
     * logga e ignora per evitare falsa sospensione.
     */
    public function handleDeleted(Subscription $stripeSub): void
    {
        $agency = Agency::where('stripe_customer_id', $stripeSub->customer)->first();

        if (!$agency) {
            Log::warning('AgencySubscriptionService: no agency for deleted subscription', [
                'subscription' => $stripeSub->id,
                'customer'     => $stripeSub->customer,
            ]);
            return;
        }

        $localSub = AgencySubscription::where('agency_id', $agency->id)->first();

        // Se la sub cancellata non è quella che trackiamo localmente,
        // è una sub orfana: ignorarla evita sospensioni errate.
        if ($localSub && $localSub->stripe_subscription_id !== $stripeSub->id) {
            Log::warning('AgencySubscriptionService: deleted subscription is not tracked — ignoring to avoid false suspension', [
                'agency_id'          => $agency->id,
                'deleted_sub'        => $stripeSub->id,
                'tracked_sub'        => $localSub->stripe_subscription_id,
                'tracked_sub_status' => $localSub->status,
            ]);
            return;
        }

        // È la subscription attiva — sospendi l'agency
        if ($localSub) {
            $localSub->update([
                'status'       => 'cancelled',
                'cancelled_at' => now(),
            ]);
        }

        $agency->update(['status' => 'suspended']);

        Log::info('Agency suspended: tracked subscription deleted', [
            'agency_id'       => $agency->id,
            'subscription_id' => $stripeSub->id,
        ]);
    }

    /**
     * Chiamato da webhook: invoice.paid.
     * Aggiorna il periodo di billing e ripristina l'agency se era sospesa per morosità.
     */
    public function handleInvoicePaid(Invoice $invoice): void
    {
        $agency = Agency::where('stripe_customer_id', $invoice->customer)->first();
        if (!$agency) return;

        $sub = AgencySubscription::where('agency_id', $agency->id)->first();
        if (!$sub) return;

        $periodEnd = $invoice->lines->data[0]->period->end ?? null;

        $sub->update([
            'status'             => 'active',
            'current_period_end' => $periodEnd
                ? Carbon::createFromTimestamp($periodEnd)
                : $sub->current_period_end,
        ]);

        if ($agency->status === 'suspended') {
            $agency->update(['status' => 'active']);
            Log::info('Agency reactivated after invoice paid', ['agency_id' => $agency->id]);
        }
    }

    /**
     * Chiamato da webhook: invoice.payment_failed.
     */
    public function handleInvoicePaymentFailed(Invoice $invoice): void
    {
        $agency = Agency::where('stripe_customer_id', $invoice->customer)->first();
        if (!$agency) return;

        AgencySubscription::where('agency_id', $agency->id)
            ->update(['status' => 'past_due']);

        Log::warning('Agency subscription past_due', [
            'agency_id' => $agency->id,
            'invoice'   => $invoice->id,
        ]);
    }

    /**
     * Crea un'AgencySubscription lifetime per agenzie AppSumo LTD.
     */
    public function createLifetime(Agency $agency): AgencySubscription
    {
        return AgencySubscription::updateOrCreate(
            ['agency_id' => $agency->id],
            [
                'plan_id'                => $agency->plan_id,
                'stripe_subscription_id' => null,
                'stripe_customer_id'     => null,
                'status'                 => 'active',
                'billing_type'           => 'lifetime',
                'current_period_start'   => now(),
                'current_period_end'     => null,
            ]
        );
    }
}
