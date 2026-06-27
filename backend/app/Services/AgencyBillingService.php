<?php

declare(strict_types=1);

namespace App\Services;

use App\Contracts\AgencyBillingServiceInterface;
use App\Models\Central\Agency;
use App\Models\Central\AgencyInvoice;
use App\Models\Central\Plan;
use Carbon\Carbon;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\Log;
use Stripe\Customer;
use Stripe\Exception\InvalidRequestException;
use Stripe\Invoice;
use Stripe\PaymentMethod;
use Stripe\SetupIntent;
use Stripe\Stripe;
use Stripe\Subscription;

class AgencyBillingService implements AgencyBillingServiceInterface
{
    public function __construct()
    {
        Stripe::setApiKey(config('services.stripe.secret'));
    }

    // ── Customer ──────────────────────────────────────────────────────────────

    public function createOrRetrieveCustomer(Agency $agency): string
    {
        if ($agency->stripe_customer_id) {
            return $agency->stripe_customer_id;
        }

        try {
            $params = [
                'email' => $agency->billing_email ?? $agency->owner?->email,
                'name' => $agency->billing_name ?? $agency->name,
                'metadata' => ['agency_id' => $agency->id],
            ];

            if ($agency->vat_number) {
                $params['tax_id_data'] = [['type' => 'eu_vat', 'value' => $agency->vat_number]];
            }

            $customer = Customer::create($params);
            $agency->update(['stripe_customer_id' => $customer->id]);

            return $customer->id;
        } catch (\Throwable $e) {
            Log::error('AgencyBillingService: createOrRetrieveCustomer failed', [
                'agency_id' => $agency->id,
                'error' => $e->getMessage(),
            ]);
            throw $e;
        }
    }

    // ── Subscription ──────────────────────────────────────────────────────────

    public function startSubscription(
        Agency $agency,
        Plan $plan,
        string $paymentMethodId,
        string $interval = 'monthly',
    ): Agency {
        try {
            $customerId = $this->createOrRetrieveCustomer($agency);

            PaymentMethod::retrieve($paymentMethodId)->attach(['customer' => $customerId]);

            Customer::update($customerId, [
                'invoice_settings' => ['default_payment_method' => $paymentMethodId],
            ]);

            $priceId = $plan->stripePriceFor($interval);
            if (! $priceId) {
                throw new \RuntimeException("No Stripe price configured for plan {$plan->id} / interval {$interval}");
            }

            $params = [
                'customer' => $customerId,
                'items' => [['price' => $priceId]],
                'default_payment_method' => $paymentMethodId,
                'expand' => ['latest_invoice.payment_intent'],
            ];

            if ($plan->trial_days > 0) {
                $params['trial_period_days'] = $plan->trial_days;
            }

            $subscription = Subscription::create($params);

            $this->syncSubscriptionFromStripe($agency, $subscription);

            Log::info('AgencyBillingService: subscription started', [
                'agency_id' => $agency->id,
                'subscription_id' => $subscription->id,
                'plan_id' => $plan->id,
                'interval' => $interval,
            ]);

            return $agency->fresh();
        } catch (\Throwable $e) {
            Log::error('AgencyBillingService: startSubscription failed', [
                'agency_id' => $agency->id,
                'plan_id' => $plan->id,
                'error' => $e->getMessage(),
            ]);
            throw $e;
        }
    }

    public function cancelSubscription(Agency $agency, bool $immediately = false): Agency
    {
        $subId = $agency->stripe_subscription_id;
        if (! $subId) {
            throw new \RuntimeException("Agency #{$agency->id} has no active Stripe subscription");
        }

        try {
            if ($immediately) {
                Subscription::retrieve($subId)->cancel();
                $agency->update(['stripe_status' => 'canceled']);
            } else {
                Subscription::update($subId, ['cancel_at_period_end' => true]);
            }

            Log::info('AgencyBillingService: subscription cancelled', [
                'agency_id' => $agency->id,
                'immediately' => $immediately,
            ]);

            return $agency->fresh();
        } catch (\Throwable $e) {
            Log::error('AgencyBillingService: cancelSubscription failed', [
                'agency_id' => $agency->id,
                'error' => $e->getMessage(),
            ]);
            throw $e;
        }
    }

    public function resumeSubscription(Agency $agency): Agency
    {
        $subId = $agency->stripe_subscription_id;
        if (! $subId) {
            throw new \RuntimeException("Agency #{$agency->id} has no Stripe subscription to resume");
        }

        try {
            Subscription::update($subId, ['cancel_at_period_end' => false]);

            Log::info('AgencyBillingService: subscription resumed', ['agency_id' => $agency->id]);

            return $agency->fresh();
        } catch (\Throwable $e) {
            Log::error('AgencyBillingService: resumeSubscription failed', [
                'agency_id' => $agency->id,
                'error' => $e->getMessage(),
            ]);
            throw $e;
        }
    }

    public function changeSubscriptionPlan(Agency $agency, Plan $newPlan): Agency
    {
        $subId = $agency->stripe_subscription_id;
        if (! $subId) {
            throw new \RuntimeException("Agency #{$agency->id} has no active Stripe subscription to change");
        }

        try {
            $stripeSub = Subscription::retrieve(['id' => $subId, 'expand' => ['items']]);
            $itemId = $stripeSub->items->data[0]->id ?? null;

            if (! $itemId) {
                throw new \RuntimeException("No subscription item found on {$subId}");
            }

            $priceId = $newPlan->stripePriceFor($agency->billing_type);
            if (! $priceId) {
                $priceId = $newPlan->stripe_price_id;
            }

            $updated = Subscription::update($subId, [
                'items' => [['id' => $itemId, 'price' => $priceId]],
                'proration_behavior' => 'create_prorations',
            ]);

            $this->syncSubscriptionFromStripe($agency, $updated);

            $agency->update(['plan_id' => $newPlan->id]);

            Log::info('AgencyBillingService: plan changed', [
                'agency_id' => $agency->id,
                'new_plan_id' => $newPlan->id,
            ]);

            return $agency->fresh();
        } catch (\Throwable $e) {
            Log::error('AgencyBillingService: changeSubscriptionPlan failed', [
                'agency_id' => $agency->id,
                'error' => $e->getMessage(),
            ]);
            throw $e;
        }
    }

    // ── Invoices ──────────────────────────────────────────────────────────────

    public function getUpcomingInvoice(Agency $agency): array
    {
        $customerId = $agency->stripe_customer_id;
        if (! $customerId) {
            return ['amount_due' => 0, 'currency' => 'eur', 'next_payment_attempt' => null, 'lines' => []];
        }

        try {
            $invoice = Invoice::upcoming(['customer' => $customerId]);

            return [
                'amount_due' => $invoice->amount_due,
                'currency' => $invoice->currency,
                'next_payment_attempt' => $invoice->next_payment_attempt,
                'lines' => collect($invoice->lines->data)->map(fn ($line) => [
                    'description' => $line->description,
                    'amount' => $line->amount,
                    'period' => [
                        'start' => $line->period->start,
                        'end' => $line->period->end,
                    ],
                ])->all(),
            ];
        } catch (InvalidRequestException $e) {
            // No upcoming invoice (e.g. cancelled subscription)
            return ['amount_due' => 0, 'currency' => 'eur', 'next_payment_attempt' => null, 'lines' => []];
        } catch (\Throwable $e) {
            Log::error('AgencyBillingService: getUpcomingInvoice failed', [
                'agency_id' => $agency->id,
                'error' => $e->getMessage(),
            ]);
            throw $e;
        }
    }

    public function listInvoices(Agency $agency): Collection
    {
        return AgencyInvoice::where('agency_id', $agency->id)
            ->orderByDesc('created_at')
            ->get();
    }

    // ── Payment Method ────────────────────────────────────────────────────────

    public function updatePaymentMethod(Agency $agency, string $paymentMethodId): Agency
    {
        $customerId = $this->createOrRetrieveCustomer($agency);

        try {
            $pm = PaymentMethod::retrieve($paymentMethodId);
            $pm->attach(['customer' => $customerId]);

            Customer::update($customerId, [
                'invoice_settings' => ['default_payment_method' => $paymentMethodId],
            ]);

            if ($agency->stripe_subscription_id) {
                Subscription::update($agency->stripe_subscription_id, [
                    'default_payment_method' => $paymentMethodId,
                ]);
            }

            $agency->update([
                'payment_method_last4' => $pm->card?->last4 ?? null,
                'payment_method_brand' => $pm->card?->brand ?? $pm->type,
            ]);

            Log::info('AgencyBillingService: payment method updated', ['agency_id' => $agency->id]);

            return $agency->fresh();
        } catch (\Throwable $e) {
            Log::error('AgencyBillingService: updatePaymentMethod failed', [
                'agency_id' => $agency->id,
                'error' => $e->getMessage(),
            ]);
            throw $e;
        }
    }

    public function createSetupIntent(Agency $agency): string
    {
        $customerId = $this->createOrRetrieveCustomer($agency);

        try {
            $intent = SetupIntent::create([
                'customer' => $customerId,
                'payment_method_types' => ['card'],
            ]);

            return $intent->client_secret;
        } catch (\Throwable $e) {
            Log::error('AgencyBillingService: createSetupIntent failed', [
                'agency_id' => $agency->id,
                'error' => $e->getMessage(),
            ]);
            throw $e;
        }
    }

    // ── Sync ──────────────────────────────────────────────────────────────────

    public function syncSubscriptionFromStripe(Agency $agency, object $stripeSubscription): Agency
    {
        $defaultPm = null;
        if (! empty($stripeSubscription->default_payment_method)) {
            try {
                $pmId = is_string($stripeSubscription->default_payment_method)
                    ? $stripeSubscription->default_payment_method
                    : $stripeSubscription->default_payment_method->id;
                $defaultPm = PaymentMethod::retrieve($pmId);
            } catch (\Throwable) {
                // non-fatal: we'll just skip the payment method sync
            }
        }

        $updates = [
            'stripe_customer_id' => $stripeSubscription->customer,
            'stripe_subscription_id' => $stripeSubscription->id,
            'stripe_status' => $stripeSubscription->status,
            'trial_ends_at' => $stripeSubscription->trial_end
                ? Carbon::createFromTimestamp($stripeSubscription->trial_end)
                : null,
            'subscription_ends_at' => $stripeSubscription->current_period_end
                ? Carbon::createFromTimestamp($stripeSubscription->current_period_end)
                : null,
        ];

        if ($defaultPm) {
            $updates['payment_method_last4'] = $defaultPm->card?->last4 ?? null;
            $updates['payment_method_brand'] = $defaultPm->card?->brand ?? $defaultPm->type;
        }

        $agency->update($updates);

        return $agency->fresh();
    }

    // ── Invoice persistence (called from webhook) ─────────────────────────────

    public function upsertInvoice(Agency $agency, object $stripeInvoice): AgencyInvoice
    {
        $lineItems = collect($stripeInvoice->lines->data ?? [])->map(fn ($line) => [
            'description' => $line->description,
            'amount' => $line->amount,
        ])->all();

        return AgencyInvoice::updateOrCreate(
            ['stripe_invoice_id' => $stripeInvoice->id],
            [
                'agency_id' => $agency->id,
                'amount_due' => $stripeInvoice->amount_due,
                'amount_paid' => $stripeInvoice->amount_paid,
                'currency' => $stripeInvoice->currency,
                'status' => $stripeInvoice->status,
                'invoice_pdf_url' => $stripeInvoice->invoice_pdf ?? null,
                'period_start' => $stripeInvoice->period_start
                    ? Carbon::createFromTimestamp($stripeInvoice->period_start)
                    : null,
                'period_end' => $stripeInvoice->period_end
                    ? Carbon::createFromTimestamp($stripeInvoice->period_end)
                    : null,
                'paid_at' => $stripeInvoice->status_transitions?->paid_at
                    ? Carbon::createFromTimestamp($stripeInvoice->status_transitions->paid_at)
                    : null,
                'line_items' => $lineItems,
            ]
        );
    }
}
