<?php

declare(strict_types=1);

namespace App\Console\Commands;

use App\Models\Central\Agency;
use App\Models\Central\AgencySubscription;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Log;
use Stripe\Stripe;
use Stripe\Subscription as StripeSubscription;

class BillingCheckAnomalies extends Command
{
    protected $signature   = 'billing:check-anomalies {--fix : Cancel orphaned Stripe subscriptions automatically}';
    protected $description = 'Detect agencies with inconsistent billing state between local DB and Stripe';

    public function handle(): int
    {
        Stripe::setApiKey(config('services.stripe.secret'));

        if (!config('services.stripe.secret')) {
            $this->error('STRIPE_SECRET not configured.');
            return self::FAILURE;
        }

        $this->info('Checking billing anomalies…');
        $anomalies = 0;

        // ── 1. Agency attiva localmente ma subscription cancelled ────────────
        $this->line('');
        $this->line('<comment>1. Agency active but subscription cancelled</comment>');

        $mismatch = Agency::where('status', 'active')
            ->whereHas('subscription', fn ($q) => $q->where('status', 'cancelled'))
            ->with('subscription')
            ->get();

        foreach ($mismatch as $agency) {
            $this->warn("  Agency #{$agency->id} ({$agency->slug}): status=active but sub status=cancelled");
            Log::warning('billing-anomaly: agency active with cancelled subscription', ['agency_id' => $agency->id]);
            $anomalies++;
        }

        if ($mismatch->isEmpty()) $this->info('  ✓ None found');

        // ── 2. Agency sospesa ma subscription attiva su Stripe ───────────────
        $this->line('');
        $this->line('<comment>2. Agency suspended but Stripe subscription may still be active</comment>');

        $suspended = Agency::where('status', 'suspended')
            ->whereHas('subscription', fn ($q) => $q->whereNotNull('stripe_subscription_id'))
            ->with('subscription')
            ->get();

        foreach ($suspended as $agency) {
            $sub = $agency->subscription;
            try {
                $stripe = StripeSubscription::retrieve($sub->stripe_subscription_id);
                if (in_array($stripe->status, ['active', 'trialing'], true)) {
                    $this->warn("  Agency #{$agency->id} ({$agency->slug}): suspended locally but Stripe sub is {$stripe->status}");
                    Log::warning('billing-anomaly: agency suspended but Stripe sub active', [
                        'agency_id'    => $agency->id,
                        'stripe_sub'   => $sub->stripe_subscription_id,
                        'stripe_status' => $stripe->status,
                    ]);
                    $anomalies++;
                }
            } catch (\Throwable $e) {
                $this->warn("  Agency #{$agency->id}: could not retrieve Stripe sub {$sub->stripe_subscription_id}: {$e->getMessage()}");
            }
        }

        if ($suspended->isEmpty()) $this->info('  ✓ None found');

        // ── 3. Agency senza subscription locale ma con stripe_customer_id ────
        $this->line('');
        $this->line('<comment>3. Agency with stripe_customer_id but no local subscription record</comment>');

        $orphan = Agency::whereNotNull('stripe_customer_id')
            ->doesntHave('subscription')
            ->get();

        foreach ($orphan as $agency) {
            $this->warn("  Agency #{$agency->id} ({$agency->slug}): stripe_customer_id={$agency->stripe_customer_id} but no AgencySubscription record");
            $anomalies++;
        }

        if ($orphan->isEmpty()) $this->info('  ✓ None found');

        // ── 4. Subscription locale con stripe_subscription_id che non esiste su Stripe ──
        $this->line('');
        $this->line('<comment>4. Local subscription pointing to non-existent Stripe subscription</comment>');

        AgencySubscription::whereNotNull('stripe_subscription_id')
            ->whereIn('status', ['active', 'trialing', 'past_due'])
            ->each(function (AgencySubscription $sub) use (&$anomalies) {
                try {
                    $stripe = StripeSubscription::retrieve($sub->stripe_subscription_id);
                    if ($stripe->status !== $sub->status) {
                        $this->warn(
                            "  Sub #{$sub->id} (agency #{$sub->agency_id}): local={$sub->status}, Stripe={$stripe->status}"
                        );
                        $anomalies++;
                    }
                } catch (\Stripe\Exception\InvalidRequestException $e) {
                    $this->error(
                        "  Sub #{$sub->id} (agency #{$sub->agency_id}): Stripe sub {$sub->stripe_subscription_id} not found — {$e->getMessage()}"
                    );
                    $anomalies++;
                } catch (\Throwable $e) {
                    $this->warn("  Sub #{$sub->id}: API error — {$e->getMessage()}");
                }
            });

        // ── Summary ──────────────────────────────────────────────────────────
        $this->line('');

        if ($anomalies === 0) {
            $this->info('✅ No billing anomalies detected.');
        } else {
            $this->error("⚠ {$anomalies} anomalies detected. Check logs for details.");
            $this->line('  Run with --fix to cancel orphaned subscriptions (not yet implemented).');
        }

        return $anomalies > 0 ? self::FAILURE : self::SUCCESS;
    }
}
