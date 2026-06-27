<?php

declare(strict_types=1);

namespace App\Jobs;

use App\Models\Central\Agency;
use App\Models\Central\AiCreditLedger;
use App\Models\Central\AiCreditPackage;
use App\Models\Central\BillingEvent;
use App\Models\Central\CommissionRecord;
use App\Models\Central\PayoutRecord;
use App\Services\AgencyBillingService;
use App\Services\AgencySubscriptionService;
use App\Services\AiCreditsService;
use App\Services\DashboardAlertService;
use Carbon\Carbon;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Log;
use Stripe\Invoice;
use Stripe\Stripe;
use Stripe\Subscription;

class ProcessStripeWebhookJob implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public int $tries = 5;

    // backoff esponenziale: 60s, 120s, 180s, 240s, 300s
    public array $backoff = [60, 120, 180, 240, 300];

    public function __construct(
        private readonly int $billingEventId,
    ) {}

    public function handle(
        AgencySubscriptionService $subscriptionService,
        AgencyBillingService $billingService,
        AiCreditsService $aiCredits,
    ): void {
        $billingEvent = BillingEvent::find($this->billingEventId);

        if (! $billingEvent) {
            Log::warning('ProcessStripeWebhookJob: BillingEvent not found', ['id' => $this->billingEventId]);

            return;
        }

        if ($billingEvent->isProcessed()) {
            return; // già processato da un dispatch precedente
        }

        try {
            $this->processEvent($billingEvent, $subscriptionService, $billingService, $aiCredits);
            $billingEvent->markProcessed();
        } catch (\Throwable $e) {
            $billingEvent->markFailed($e->getMessage());
            Log::error('ProcessStripeWebhookJob failed', [
                'billing_event_id' => $this->billingEventId,
                'event_type' => $billingEvent->event_type,
                'error' => $e->getMessage(),
                'attempt' => $this->attempts(),
            ]);
            throw $e; // re-throw per attivare il retry della queue
        }
    }

    // ── Event router ──────────────────────────────────────────────────────────

    private function processEvent(
        BillingEvent $billingEvent,
        AgencySubscriptionService $subscriptionService,
        AgencyBillingService $billingService,
        AiCreditsService $aiCredits,
    ): void {
        $payload = $billingEvent->payload;
        $type = $billingEvent->event_type;
        $obj = $payload['data']['object'] ?? [];

        match ($type) {
            'payment_intent.succeeded' => $this->onPaymentIntentSucceeded($obj),
            'payment_intent.payment_failed' => $this->onPaymentIntentFailed($obj),
            'customer.subscription.created',
            'customer.subscription.updated' => $this->onSubscriptionUpsert($obj, $subscriptionService, $billingService),
            'customer.subscription.deleted' => $this->onSubscriptionDeleted($obj, $subscriptionService),
            'customer.subscription.trial_will_end' => $this->onTrialWillEnd($obj),
            'invoice.paid',
            'invoice.payment_succeeded' => $this->onInvoicePaid($obj, $subscriptionService, $billingService),
            'invoice.payment_failed' => $this->onInvoicePaymentFailed($obj, $subscriptionService),
            'checkout.session.completed' => $this->onCheckoutCompleted($obj, $aiCredits, $subscriptionService),
            'payment_method.attached' => $this->onPaymentMethodAttached($obj),
            'customer.updated' => $this->onCustomerUpdated($obj),
            'account.updated' => $this->onAccountUpdated($obj),
            'charge.refunded' => $this->onChargeRefunded($obj),
            'charge.dispute.created' => $this->onDisputeCreated($obj),
            'payout.created',
            'payout.paid',
            'payout.failed',
            'payout.canceled' => $this->onPayoutUpsert($obj, $payload['account'] ?? null, $billingEvent),
            default => null,
        };
    }

    // ── Event handlers ────────────────────────────────────────────────────────

    private function onPaymentIntentSucceeded(array $obj): void
    {
        $piId = $obj['id'] ?? null;
        if (! $piId) {
            return;
        }

        $updated = CommissionRecord::where('stripe_payment_intent_id', $piId)
            ->where('status', CommissionRecord::STATUS_PENDING)
            ->update([
                'status' => CommissionRecord::STATUS_SETTLED,
                'stripe_charge_id' => $obj['latest_charge'] ?? null,
                'settled_at' => now(),
            ]);

        Log::info('CommissionRecord settled', ['payment_intent' => $piId, 'rows' => $updated]);
    }

    private function onPaymentIntentFailed(array $obj): void
    {
        $piId = $obj['id'] ?? null;
        if (! $piId) {
            return;
        }

        CommissionRecord::where('stripe_payment_intent_id', $piId)
            ->where('status', CommissionRecord::STATUS_PENDING)
            ->update(['status' => CommissionRecord::STATUS_FAILED]);
    }

    private function onSubscriptionUpsert(
        array $obj,
        AgencySubscriptionService $svc,
        AgencyBillingService $billingService,
    ): void {
        try {
            $stripeSub = Subscription::constructFrom($obj);
            $svc->syncFromStripe($stripeSub);

            // Also sync Agency billing fields (stripe_status, dates, payment method)
            $agency = Agency::where('stripe_customer_id', $obj['customer'] ?? null)->first();
            if ($agency) {
                $billingService->syncSubscriptionFromStripe($agency, $stripeSub);
            }
        } catch (\Throwable $e) {
            Log::warning('subscription upsert sync failed', [
                'obj_id' => $obj['id'] ?? null,
                'error' => $e->getMessage(),
            ]);
        }
    }

    private function onTrialWillEnd(array $obj): void
    {
        $customerId = $obj['customer'] ?? null;
        if (! $customerId) {
            return;
        }

        $agency = Agency::where('stripe_customer_id', $customerId)->first();
        if (! $agency) {
            return;
        }

        Log::info('AgencySubscription: trial will end', [
            'agency_id' => $agency->id,
            'trial_end' => $obj['trial_end'] ?? null,
        ]);

        // DashboardAlertService can surface this as an alert type if configured
    }

    private function onSubscriptionDeleted(array $obj, AgencySubscriptionService $svc): void
    {
        // NON swallow: la sospensione dell'agency è critica e deve andare a buon fine
        $stripeSub = Subscription::constructFrom($obj);
        $svc->handleDeleted($stripeSub);
    }

    private function onInvoicePaid(
        array $obj,
        AgencySubscriptionService $svc,
        AgencyBillingService $billingService,
    ): void {
        try {
            $invoice = Invoice::constructFrom($obj);
            $svc->handleInvoicePaid($invoice);

            // Persist invoice record
            $agency = Agency::where('stripe_customer_id', $obj['customer'] ?? null)->first();
            if ($agency) {
                $billingService->upsertInvoice($agency, $invoice);
            }
        } catch (\Throwable $e) {
            Log::warning('invoice.paid handling failed', ['error' => $e->getMessage()]);
        }
    }

    private function onInvoicePaymentFailed(array $obj, AgencySubscriptionService $svc): void
    {
        try {
            $invoice = Invoice::constructFrom($obj);
            $svc->handleInvoicePaymentFailed($invoice);
        } catch (\Throwable $e) {
            Log::warning('invoice.payment_failed handling failed', ['error' => $e->getMessage()]);
        }
    }

    private function onPaymentMethodAttached(array $obj): void
    {
        $customerId = $obj['customer'] ?? null;
        if (! $customerId) {
            return;
        }

        $agency = Agency::where('stripe_customer_id', $customerId)->first();
        if (! $agency) {
            return;
        }

        $agency->update([
            'payment_method_last4' => $obj['card']['last4'] ?? null,
            'payment_method_brand' => $obj['card']['brand'] ?? $obj['type'] ?? null,
        ]);
    }

    private function onCustomerUpdated(array $obj): void
    {
        $customerId = $obj['id'] ?? null;
        if (! $customerId) {
            return;
        }

        $agency = Agency::where('stripe_customer_id', $customerId)->first();
        if (! $agency) {
            return;
        }

        $updates = [];
        if (! empty($obj['email'])) {
            $updates['billing_email'] = $obj['email'];
        }
        if (! empty($obj['name'])) {
            $updates['billing_name'] = $obj['name'];
        }

        if ($updates) {
            $agency->update($updates);
        }
    }

    private function onCheckoutCompleted(array $obj, AiCreditsService $aiCredits, AgencySubscriptionService $subscriptionService): void
    {
        $metadata = $obj['metadata'] ?? [];
        $type = $metadata['type'] ?? '';

        if ($type === 'agency_subscription') {
            $agency = Agency::find($metadata['agency_id'] ?? null);
            if (! $agency) {
                Log::warning('checkout.session.completed: agency not found for subscription', $metadata);

                return;
            }

            // Set stripe_customer_id so subsequent subscription webhooks can find the agency
            if (! $agency->stripe_customer_id && ! empty($obj['customer'])) {
                $agency->update(['stripe_customer_id' => $obj['customer']]);
            }

            // Immediately sync the subscription rather than waiting for webhook retry
            $stripeSubId = $obj['subscription'] ?? null;
            if ($stripeSubId) {
                Stripe::setApiKey(config('services.stripe.secret'));
                $stripeSub = Subscription::retrieve($stripeSubId);
                $subscriptionService->syncFromStripe($stripeSub);
            }

            return;
        }

        if ($type !== 'ai_credits') {
            return;
        }

        $agency = Agency::find($metadata['agency_id'] ?? null);
        $package = AiCreditPackage::find($metadata['package_id'] ?? null);

        if (! $agency || ! $package) {
            Log::warning('checkout.session.completed: agency or package not found', $metadata);

            return;
        }

        $paymentIntentId = $obj['payment_intent'] ?? $obj['id'];

        // Idempotenza: non credita due volte lo stesso payment_intent
        if (AiCreditLedger::where('stripe_payment_intent_id', $paymentIntentId)->exists()) {
            Log::info('AI credits already credited, skipping', ['payment_intent' => $paymentIntentId]);

            return;
        }

        $aiCredits->purchase($agency, $package, $paymentIntentId);
    }

    private function onAccountUpdated(array $obj): void
    {
        $accountId = $obj['id'] ?? null;
        if (! $accountId) {
            return;
        }

        $detailsSubmitted = (bool) ($obj['details_submitted'] ?? false);
        $currentlyDue = $obj['requirements']['currently_due'] ?? [];

        Agency::where('stripe_connect_account_id', $accountId)
            ->update(['stripe_connect_onboarded' => $detailsSubmitted && empty($currentlyDue)]);
    }

    private function onChargeRefunded(array $obj): void
    {
        $chargeId = $obj['id'] ?? null;
        if (! $chargeId) {
            return;
        }

        $original = CommissionRecord::where('stripe_charge_id', $chargeId)
            ->where('status', CommissionRecord::STATUS_SETTLED)
            ->first();

        if (! $original) {
            return;
        }

        $refundedCents = (int) ($obj['amount_refunded'] ?? 0);
        if ($refundedCents <= 0) {
            return;
        }

        $original->createRefund($refundedCents, 'Stripe refund on charge '.$chargeId);
        $original->forceSetStatus(CommissionRecord::STATUS_REFUNDED);
    }

    private function onDisputeCreated(array $obj): void
    {
        $chargeId = $obj['charge'] ?? null;
        if (! $chargeId) {
            return;
        }

        CommissionRecord::where('stripe_charge_id', $chargeId)
            ->update(['status' => CommissionRecord::STATUS_DISPUTED]);

        Log::warning('Dispute opened on charge', ['charge_id' => $chargeId]);
    }

    /**
     * Upserts a PayoutRecord from a payout.* event.
     *
     * Agency is resolved via stripe_connect_account_id, which is in the top-level
     * `account` field of Connect events (not inside data.object).
     */
    private function onPayoutUpsert(array $obj, ?string $connectAccountId, BillingEvent $billingEvent): void
    {
        if (! $connectAccountId) {
            Log::warning('onPayoutUpsert: missing Connect account in event', ['payout_id' => $obj['id'] ?? null]);

            return;
        }

        $agency = Agency::where('stripe_connect_account_id', $connectAccountId)->first();

        if (! $agency) {
            Log::warning('onPayoutUpsert: no agency for Connect account', [
                'account' => $connectAccountId,
                'payout_id' => $obj['id'] ?? null,
            ]);

            return;
        }

        // Stamp agency_id on the BillingEvent so it surfaces in the billing history.
        if (! $billingEvent->agency_id) {
            $billingEvent->update(['agency_id' => $agency->id]);
        }

        $statusMap = [
            'pending' => PayoutRecord::STATUS_PENDING,
            'in_transit' => PayoutRecord::STATUS_IN_TRANSIT,
            'paid' => PayoutRecord::STATUS_PAID,
            'failed' => PayoutRecord::STATUS_FAILED,
            'canceled' => PayoutRecord::STATUS_CANCELLED,
        ];

        $stripeStatus = $obj['status'] ?? 'pending';

        PayoutRecord::updateOrCreate(
            ['stripe_payout_id' => $obj['id']],
            [
                'agency_id' => $agency->id,
                'stripe_connect_account_id' => $connectAccountId,
                'amount_cents' => (int) ($obj['amount'] ?? 0),
                'currency' => strtolower($obj['currency'] ?? 'eur'),
                'status' => $statusMap[$stripeStatus] ?? $stripeStatus,
                'arrival_date' => isset($obj['arrival_date'])
                                                ? Carbon::createFromTimestamp((int) $obj['arrival_date'])->toDateString()
                                                : null,
                'failure_reason' => $obj['failure_message'] ?? null,
                'metadata' => $obj['metadata'] ?? [],
            ],
        );
    }
}
