<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Models\Central\Agency;
use App\Models\Central\AiCreditLedger;
use App\Models\Central\AiCreditPackage;
use App\Services\AiCreditsService;
use Illuminate\Http\Request;
use Illuminate\Http\Response;
use Stripe\Event;
use Stripe\Stripe;
use Stripe\Webhook;

class StripeWebhookController extends Controller
{
    public function __construct(private readonly AiCreditsService $aiCredits) {}

    public function handle(Request $request): Response
    {
        Stripe::setApiKey(config('services.stripe.secret'));

        try {
            $event = Webhook::constructEvent(
                $request->getContent(),
                $request->header('Stripe-Signature'),
                config('services.stripe.webhook_secret')
            );
        } catch (\Throwable $e) {
            return response('Invalid signature', 400);
        }

        match ($event->type) {
            'account.updated' => $this->handleAccountUpdated($event),
            'payment_intent.succeeded' => $this->handlePaymentIntentSucceeded($event),
            'customer.subscription.deleted' => $this->handleSubscriptionDeleted($event),
            'checkout.session.completed' => $this->handleCheckoutCompleted($event),
            default => null,
        };

        return response('OK', 200);
    }

    private function handleAccountUpdated(Event $event): void
    {
        $account = $event->data->object;
        Agency::where('stripe_connect_account_id', $account->id)
            ->update([
                'stripe_connect_onboarded' => $account->details_submitted && empty($account->requirements->currently_due),
            ]);
    }

    private function handlePaymentIntentSucceeded(Event $event): void
    {
        // Log transaction — extend as needed for analytics
    }

    private function handleSubscriptionDeleted(Event $event): void
    {
        $subscription = $event->data->object;
        // Find agency by Stripe customer and suspend if plan expired
        // Implementation depends on how subscriptions are linked
    }

    private function handleCheckoutCompleted(Event $event): void
    {
        $session = $event->data->object;
        $metadata = $session->metadata ?? [];

        if (($metadata['type'] ?? '') !== 'ai_credits') {
            return;
        }

        $agency = Agency::find($metadata['agency_id'] ?? null);
        $package = AiCreditPackage::find($metadata['package_id'] ?? null);

        if ($agency && $package) {
            $this->aiCredits->purchase($agency, $package, $session->payment_intent ?? $session->id);
        }
    }
}
