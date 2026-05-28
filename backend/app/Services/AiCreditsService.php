<?php

declare(strict_types=1);

namespace App\Services;

use App\Exceptions\InsufficientCreditsException;
use App\Models\Central\Agency;
use App\Models\Central\AiCreditLedger;
use App\Models\Central\AiCreditPackage;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Mail;
use Stripe\Checkout\Session;
use Stripe\Stripe;

class AiCreditsService
{
    public function getBalance(Agency $agency): int
    {
        return (int) AiCreditLedger::where('agency_id', $agency->id)->sum('amount');
    }

    public function hasCredits(Agency $agency, int $required = 1): bool
    {
        return $this->getBalance($agency) >= $required;
    }

    public function consume(Agency $agency, int $credits, string $description, ?string $tenantId = null): bool
    {
        return DB::connection('central')->transaction(function () use ($agency, $credits, $description, $tenantId) {
            $balance = $this->getBalance($agency);

            if ($balance < $credits) {
                throw new InsufficientCreditsException($balance, $credits);
            }

            $balanceAfter = $balance - $credits;

            AiCreditLedger::create([
                'agency_id' => $agency->id,
                'tenant_id' => $tenantId,
                'amount' => -$credits,
                'balance_after' => $balanceAfter,
                'type' => AiCreditLedger::TYPE_CONSUMPTION,
                'description' => $description,
                'created_at' => now(),
            ]);

            return true;
        });
    }

    public function purchase(Agency $agency, AiCreditPackage $package, string $paymentIntentId): void
    {
        DB::connection('central')->transaction(function () use ($agency, $package, $paymentIntentId) {
            $balance = $this->getBalance($agency);
            $balanceAfter = $balance + $package->credits;

            AiCreditLedger::create([
                'agency_id' => $agency->id,
                'tenant_id' => null,
                'amount' => $package->credits,
                'balance_after' => $balanceAfter,
                'type' => AiCreditLedger::TYPE_PURCHASE,
                'description' => "Purchase: {$package->name}",
                'stripe_payment_intent_id' => $paymentIntentId,
                'created_at' => now(),
            ]);
        });
    }

    public function addBonus(Agency $agency, int $credits, string $reason = 'Manual bonus'): void
    {
        $balance = $this->getBalance($agency);

        AiCreditLedger::create([
            'agency_id' => $agency->id,
            'amount' => $credits,
            'balance_after' => $balance + $credits,
            'type' => AiCreditLedger::TYPE_BONUS,
            'description' => $reason,
            'created_at' => now(),
        ]);
    }

    public function applyMonthlyBonus(): void
    {
        Agency::active()
            ->with('plan')
            ->each(function (Agency $agency) {
                $bonus = (int) ($agency->plan?->limits['ai_credits_monthly_bonus'] ?? 0);
                if ($bonus > 0) {
                    $this->addBonus($agency, $bonus, 'Monthly plan bonus');
                }
            });
    }

    public function createCheckoutSession(Agency $agency, AiCreditPackage $package): Session
    {
        Stripe::setApiKey(config('services.stripe.secret'));

        return Session::create([
            'payment_method_types' => ['card'],
            'mode' => 'payment',
            'line_items' => [[
                'price' => $package->stripe_price_id,
                'quantity' => 1,
            ]],
            'metadata' => [
                'agency_id' => $agency->id,
                'package_id' => $package->id,
                'type' => 'ai_credits',
            ],
            'success_url' => url('/central/api/ai-credits/success?session_id={CHECKOUT_SESSION_ID}'),
            'cancel_url' => url('/credits/buy'),
        ]);
    }
}
