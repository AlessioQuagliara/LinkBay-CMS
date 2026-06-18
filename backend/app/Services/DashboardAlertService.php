<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Central\Agency;
use App\Models\Central\AgencyMember;
use App\Models\Central\Tenant;
use App\Models\Central\TermsAcceptance;
use Illuminate\Support\Collection;

/**
 * Resolves the set of operational alerts to display on the Agency dashboard.
 *
 * Only owner and admin members receive alerts — regular members cannot act on
 * any of these states, so surfacing them adds no value.
 *
 * Ordering: lower priority number = higher urgency = shown first.
 *  10–11  subscription health (danger)
 *  20–21  Stripe Connect status (warning)
 *  30     AI credits balance (warning)
 *  40     terms acceptance (info)
 *  50     no stores yet (info)
 */
class DashboardAlertService
{
    public const LOW_CREDITS_THRESHOLD = 100;

    public function __construct(private readonly AiCreditsService $aiCredits) {}

    /**
     * @return Collection<int, AlertItem>
     */
    public function resolve(Agency $agency, ?AgencyMember $member): Collection
    {
        if (! $member?->isOwnerOrAdmin()) {
            return collect();
        }

        $agency->loadMissing('subscription');

        $alerts = [];

        $this->addSubscriptionAlerts($alerts, $agency);
        $this->addStripeAlerts($alerts, $agency);
        $this->addAiCreditsAlert($alerts, $agency);
        $this->addTermsAlert($alerts, $agency);
        $this->addNoStoresAlert($alerts, $agency);

        return collect($alerts)->sortBy('priority')->values();
    }

    // ── Alert builders ────────────────────────────────────────────────────────

    /**
     * @param  AlertItem[]  $alerts
     */
    private function addSubscriptionAlerts(array &$alerts, Agency $agency): void
    {
        $sub = $agency->subscription;

        if (! $sub) {
            return;
        }

        if ($sub->isPastDue()) {
            $alerts[] = new AlertItem(
                key: 'subscription_past_due',
                severity: 'danger',
                title: 'Pagamento abbonamento in ritardo',
                body: 'Il rinnovo del tuo abbonamento non è andato a buon fine. Aggiorna il metodo di pagamento per evitare l\'interruzione del servizio.',
                ctaLabel: 'Gestisci abbonamento',
                ctaRoute: 'filament.agency.pages.agency-billing',
                priority: 10,
                ctaOwnerOnly: true,
            );

            return;
        }

        if ($sub->status === 'canceled' && ! $sub->isLifetime()) {
            $alerts[] = new AlertItem(
                key: 'subscription_cancelled',
                severity: 'danger',
                title: 'Abbonamento cancellato',
                body: 'Il tuo abbonamento è stato cancellato. Rinnova per continuare ad accedere a tutte le funzionalità.',
                ctaLabel: 'Rinnova abbonamento',
                ctaRoute: 'filament.agency.pages.agency-billing',
                priority: 11,
                ctaOwnerOnly: true,
            );
        }
    }

    /**
     * @param  AlertItem[]  $alerts
     */
    private function addStripeAlerts(array &$alerts, Agency $agency): void
    {
        if (! $agency->stripe_connect_account_id) {
            $alerts[] = new AlertItem(
                key: 'stripe_not_configured',
                severity: 'warning',
                title: 'Stripe Connect non configurato',
                body: 'Collega un account Stripe per ricevere pagamenti e payout dai tuoi store.',
                ctaLabel: 'Configura Stripe',
                ctaRoute: 'filament.agency.pages.agency-settings',
                priority: 20,
            );

            return;
        }

        if (! $agency->stripe_connect_onboarded) {
            $alerts[] = new AlertItem(
                key: 'stripe_not_onboarded',
                severity: 'warning',
                title: 'Verifica Stripe incompleta',
                body: 'Il tuo account Stripe Connect non ha completato la verifica. I payout sono sospesi fino al completamento.',
                ctaLabel: 'Completa verifica',
                ctaRoute: 'filament.agency.pages.agency-settings',
                priority: 21,
            );
        }
    }

    /**
     * @param  AlertItem[]  $alerts
     */
    private function addAiCreditsAlert(array &$alerts, Agency $agency): void
    {
        $balance = $this->aiCredits->getBalance($agency);

        if ($balance <= self::LOW_CREDITS_THRESHOLD) {
            $alerts[] = new AlertItem(
                key: 'ai_credits_low',
                severity: 'warning',
                title: 'Crediti AI in esaurimento',
                body: "Saldo attuale: {$balance} ".($balance === 1 ? 'credito' : 'crediti').'. Ricarica per continuare a usare le funzionalità AI nei tuoi store.',
                ctaLabel: 'Acquista crediti',
                ctaRoute: 'filament.agency.pages.ai-credits',
                priority: 30,
            );
        }
    }

    /**
     * @param  AlertItem[]  $alerts
     */
    private function addTermsAlert(array &$alerts, Agency $agency): void
    {
        if (! TermsAcceptance::hasAccepted($agency->id)) {
            $alerts[] = new AlertItem(
                key: 'terms_pending',
                severity: 'info',
                title: 'Termini di servizio da accettare',
                body: 'È disponibile una nuova versione dei termini di servizio. Accettali per continuare a usare la piattaforma.',
                ctaLabel: 'Leggi e accetta',
                ctaRoute: 'filament.agency.pages.terms-acceptance',
                priority: 40,
            );
        }
    }

    /**
     * @param  AlertItem[]  $alerts
     */
    private function addNoStoresAlert(array &$alerts, Agency $agency): void
    {
        // Only relevant when the agency has a plan — without one, PlanUpsellWidget
        // already prompts the user to subscribe before thinking about stores.
        if (! $agency->plan_id) {
            return;
        }

        $storeCount = Tenant::where('agency_id', $agency->id)
            ->where('status', 'active')
            ->count();

        if ($storeCount === 0) {
            $alerts[] = new AlertItem(
                key: 'no_stores',
                severity: 'info',
                title: 'Nessun negozio attivo',
                body: 'Non hai ancora creato alcun negozio. Crea il tuo primo store per iniziare.',
                ctaLabel: 'Crea un negozio',
                ctaRoute: 'filament.agency.resources.stores.index',
                priority: 50,
            );
        }
    }
}
