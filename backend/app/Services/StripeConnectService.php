<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Central\Agency;
use App\Models\Central\CommissionRecord;
use Stripe\Account;
use Stripe\AccountLink;
use Stripe\PaymentIntent;
use Stripe\Stripe;

class StripeConnectService
{
    public function __construct(
        private readonly PlatformFeeService $feeService,
    ) {
        Stripe::setApiKey(config('services.stripe.secret'));
    }

    public function createOnboardingLink(Agency $agency): string
    {
        if (!$agency->stripe_connect_account_id) {
            $account = Account::create(['type' => 'express']);
            $agency->update(['stripe_connect_account_id' => $account->id]);
        }

        $link = AccountLink::create([
            'account'     => $agency->stripe_connect_account_id,
            'refresh_url' => route('agency.stripe.onboard.refresh'),
            'return_url'  => route('agency.stripe.onboard.return'),
            'type'        => 'account_onboarding',
        ]);

        return $link->url;
    }

    public function isOnboarded(Agency $agency): bool
    {
        if (!$agency->stripe_connect_account_id) {
            return false;
        }

        $account = Account::retrieve($agency->stripe_connect_account_id);

        return $account->details_submitted && !$account->requirements->currently_due;
    }

    public function syncOnboardingStatus(): void
    {
        Agency::active()
            ->whereNotNull('stripe_connect_account_id')
            ->where('stripe_connect_onboarded', false)
            ->each(function (Agency $agency) {
                try {
                    if ($this->isOnboarded($agency)) {
                        $agency->update(['stripe_connect_onboarded' => true]);
                    }
                } catch (\Throwable) {
                    // silently skip API errors
                }
            });
    }

    /**
     * Crea un PaymentIntent con application fee a favore di LinkBay.
     *
     * Flusso (Stripe call FUORI dalla DB transaction):
     * 1. Risolve la regola fee attiva
     * 2. Salva CommissionRecord (snapshot fee) — committed immediatamente
     * 3. Crea PaymentIntent su Stripe — la metadata include commission_record_id per recovery
     * 4. Aggiorna CommissionRecord con stripe_payment_intent_id
     *
     * Recovery:
     * - Se Stripe fallisce al passo 3: CommissionRecord viene eliminato (cleanup)
     * - Se il passo 4 fallisce: il webhook payment_intent.succeeded può trovare il record
     *   tramite metadata.commission_record_id
     */
    public function createPaymentWithFee(
        Agency $agency,
        int $amountCents,
        string $currency,
        string $description,
        ?string $tenantId = null,
    ): PaymentIntent {
        $rule     = $this->feeService->resolveRule($agency);
        $feeCents = $this->feeService->calculateFee($amountCents, $rule);
        $netCents = $this->feeService->calculateNet($amountCents, $feeCents);

        // Step 1: salva il CommissionRecord PRIMA di toccare Stripe
        // Committed immediatamente — non dentro una transazione aperta
        $commission = CommissionRecord::create([
            'agency_id'            => $agency->id,
            'tenant_id'            => $tenantId,
            'platform_fee_rule_id' => $rule->id,
            'gross_amount_cents'   => $amountCents,
            'fee_pct'              => $rule->fee_pct,
            'fee_amount_cents'     => $feeCents,
            'net_to_agency_cents'  => $netCents,
            'currency'             => strtolower($currency),
            'status'               => CommissionRecord::STATUS_PENDING,
        ]);

        try {
            // Step 2: chiama Stripe fuori da qualsiasi transazione DB aperta
            $intent = PaymentIntent::create([
                'amount'                 => $amountCents,
                'currency'               => strtolower($currency),
                'description'            => $description,
                'application_fee_amount' => $feeCents,
                'transfer_data'          => [
                    'destination' => $agency->stripe_connect_account_id,
                ],
                'metadata' => [
                    'agency_id'            => $agency->id,
                    'commission_record_id' => $commission->id,
                    'tenant_id'            => $tenantId,
                ],
            ]);

            // Step 3: collega il CommissionRecord al PaymentIntent
            // Se questo fallisce, il webhook usa metadata.commission_record_id per il recovery
            $commission->update(['stripe_payment_intent_id' => $intent->id]);

            return $intent;
        } catch (\Throwable $e) {
            // Se Stripe non ha ancora creato il PaymentIntent, elimina il record orfano
            $commission->delete();
            throw $e;
        }
    }
}
