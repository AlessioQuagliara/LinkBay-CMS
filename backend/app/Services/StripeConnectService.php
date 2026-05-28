<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Central\Agency;
use Stripe\Account;
use Stripe\AccountLink;
use Stripe\PaymentIntent;
use Stripe\Stripe;

class StripeConnectService
{
    public function __construct()
    {
        Stripe::setApiKey(config('services.stripe.secret'));
    }

    public function createOnboardingLink(Agency $agency): string
    {
        if (!$agency->stripe_connect_account_id) {
            $account = Account::create(['type' => 'express']);
            $agency->update(['stripe_connect_account_id' => $account->id]);
        }

        $link = AccountLink::create([
            'account' => $agency->stripe_connect_account_id,
            'refresh_url' => route('agency.stripe.onboard.refresh'),
            'return_url' => route('agency.stripe.onboard.return'),
            'type' => 'account_onboarding',
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
                    $onboarded = $this->isOnboarded($agency);
                    if ($onboarded) {
                        $agency->update(['stripe_connect_onboarded' => true]);
                    }
                } catch (\Throwable) {
                    // silently skip API errors
                }
            });
    }

    public function createPaymentWithFee(
        Agency $agency,
        int $amountCents,
        string $currency,
        string $description
    ): PaymentIntent {
        $feeCents = (int) round($amountCents * ($agency->transactionFeePct() / 100));

        return PaymentIntent::create([
            'amount' => $amountCents,
            'currency' => strtolower($currency),
            'description' => $description,
            'application_fee_amount' => $feeCents,
            'transfer_data' => [
                'destination' => $agency->stripe_connect_account_id,
            ],
        ]);
    }
}
