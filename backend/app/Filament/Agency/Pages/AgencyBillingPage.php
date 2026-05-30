<?php

declare(strict_types=1);

namespace App\Filament\Agency\Pages;

use App\Filament\Agency\Concerns\ResolvesCurrentAgency;
use App\Models\Central\AgencySubscription;
use App\Models\Central\Plan;
use App\Services\AgencySubscriptionService;
use Filament\Notifications\Notification;
use Filament\Pages\Page;
use Illuminate\Support\Collection;
use Stripe\Checkout\Session;
use Stripe\Stripe;

class AgencyBillingPage extends Page
{
    use ResolvesCurrentAgency;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-credit-card';
    protected static ?string $navigationLabel = 'Abbonamento';
    protected static ?string $slug = 'agency-billing';
    protected string $view = 'filament.agency.pages.agency-billing';

    // ── Piano corrente ────────────────────────────────────────────────────────

    public function planName(): string
    {
        return $this->agency()?->plan?->name ?? '—';
    }

    public function planPrice(): string
    {
        $agency = $this->agency();
        if (!$agency?->plan) return '—';
        if ($agency->billing_type === 'lifetime') return 'Lifetime (AppSumo)';
        $interval = $agency->plan->billing_interval === 'year' ? 'anno' : 'mese';
        return '€' . number_format((float) $agency->plan->price, 2, ',', '.') . ' / ' . $interval;
    }

    public function maxStores(): string
    {
        $max = $this->agency()?->plan?->limits['max_stores'] ?? null;
        return $max === null ? 'Illimitati' : (string) $max;
    }

    public function transactionFee(): string
    {
        $pct = $this->agency()?->transactionFeePct() ?? 0.0;
        return $pct . '%';
    }

    public function features(): array
    {
        return $this->agency()?->plan?->limits ?? [];
    }

    public function isLifetime(): bool
    {
        return $this->agency()?->billing_type === 'lifetime';
    }

    public function hasActivePlan(): bool
    {
        return $this->agency()?->plan_id !== null;
    }

    public function subscription(): ?AgencySubscription
    {
        $agency = $this->agency();
        return $agency ? AgencySubscription::where('agency_id', $agency->id)->first() : null;
    }

    // ── Piani disponibili per sottoscrizione ──────────────────────────────────

    public function availablePlans(): Collection
    {
        return Plan::where('is_active', true)
            ->whereNotNull('stripe_price_id')   // solo piani acquistabili via Stripe
            ->where('slug', '!=', 'lifetime-ltd') // LTD non è sottoscrivibile online
            ->orderBy('sort_order')
            ->orderBy('price')
            ->get();
    }

    public function isStripeConfigured(): bool
    {
        return !empty(config('services.stripe.secret'));
    }

    // ── Stripe Checkout per abbonamento ───────────────────────────────────────

    /**
     * Sottoscrive o cambia piano.
     * - Se l'agency ha già una subscription Stripe attiva: aggiorna il price esistente
     *   (nessuna nuova subscription — niente doppioni su Stripe).
     * - Se non ha subscription attiva: crea nuova sessione Checkout.
     *
     * Chiamato via wire:click="subscribe(planId)".
     */
    public function subscribe(int $planId): void
    {
        $agency = $this->agency();
        if (!$agency) {
            Notification::make()->title('Errore: agency non trovata')->danger()->send();
            return;
        }

        $plan = Plan::find($planId);
        if (!$plan || !$plan->stripe_price_id) {
            Notification::make()->title('Piano non disponibile')->danger()->send();
            return;
        }

        if (!$this->isStripeConfigured()) {
            Notification::make()->title('Stripe non configurato — contatta il supporto')->warning()->send();
            return;
        }

        // ── Branch: subscription esistente → update, no nuova checkout ──────────
        $activeSub = AgencySubscription::where('agency_id', $agency->id)
            ->whereNotNull('stripe_subscription_id')
            ->whereIn('status', ['active', 'trialing', 'past_due'])
            ->first();

        if ($activeSub) {
            try {
                app(AgencySubscriptionService::class)->changeAgencyPlan($agency, $plan);

                Notification::make()
                    ->title("Piano cambiato a {$plan->name}")
                    ->body('L\'aggiornamento è attivo immediatamente. La proroga verrà applicata nella prossima fattura.')
                    ->success()
                    ->send();
            } catch (\Throwable $e) {
                Notification::make()
                    ->title('Errore nel cambio piano: ' . $e->getMessage())
                    ->danger()
                    ->send();
            }
            return;
        }

        // ── Branch: nessuna subscription attiva → nuova Checkout Session ────────
        try {
            Stripe::setApiKey(config('services.stripe.secret'));

            $params = [
                'mode'                 => 'subscription',
                'payment_method_types' => ['card'],
                'line_items'           => [['price' => $plan->stripe_price_id, 'quantity' => 1]],
                'success_url'          => route('filament.agency.pages.agency-billing') . '?subscribed=1',
                'cancel_url'           => route('filament.agency.pages.agency-billing'),
                'metadata'             => [
                    'agency_id' => $agency->id,
                    'plan_id'   => $plan->id,
                    'type'      => 'agency_subscription',
                ],
            ];

            if ($agency->stripe_customer_id) {
                $params['customer'] = $agency->stripe_customer_id;
            } else {
                $owner = $agency->owner;
                if ($owner?->email) {
                    $params['customer_email'] = $owner->email;
                }
            }

            $session = Session::create($params);
            $this->redirect($session->url, navigate: false);
        } catch (\Throwable $e) {
            Notification::make()
                ->title('Errore Stripe: ' . $e->getMessage())
                ->danger()
                ->send();
        }
    }

    /**
     * Link al Stripe Customer Portal per gestire abbonamento esistente.
     */
    public function openCustomerPortal(): void
    {
        $agency = $this->agency();
        if (!$agency?->stripe_customer_id || !$this->isStripeConfigured()) {
            Notification::make()->title('Portale non disponibile')->warning()->send();
            return;
        }

        try {
            Stripe::setApiKey(config('services.stripe.secret'));

            $session = \Stripe\BillingPortal\Session::create([
                'customer'   => $agency->stripe_customer_id,
                'return_url' => route('filament.agency.pages.agency-billing'),
            ]);

            $this->redirect($session->url, navigate: false);
        } catch (\Throwable $e) {
            Notification::make()
                ->title('Errore portale: ' . $e->getMessage())
                ->danger()
                ->send();
        }
    }
}
