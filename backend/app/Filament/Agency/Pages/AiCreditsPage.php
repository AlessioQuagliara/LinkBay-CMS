<?php

declare(strict_types=1);

namespace App\Filament\Agency\Pages;

use App\Filament\Agency\Concerns\ResolvesCurrentAgency;
use App\Models\Central\AiCreditLedger;
use App\Models\Central\AiCreditPackage;
use App\Services\AiCreditsService;
use Carbon\Carbon;
use Filament\Notifications\Notification;
use Filament\Pages\Page;
use Illuminate\Support\Collection;

class AiCreditsPage extends Page
{
    use ResolvesCurrentAgency;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-sparkles';

    protected static ?string $navigationLabel = 'Crediti AI';

    protected static ?string $slug = 'ai-credits';

    protected string $view = 'filament.agency.pages.ai-credits';

    /** '30d' | '90d' | 'all' — controls the per-store usage breakdown window. */
    public string $filterPeriod = '30d';

    public function mount(): void
    {
        if (request()->query('purchased') === '1') {
            Notification::make()
                ->title('Crediti acquistati!')
                ->body('I crediti verranno accreditati entro pochi secondi.')
                ->success()
                ->send();
        }
    }

    public function balance(): int
    {
        $agency = $this->agency();

        return $agency ? app(AiCreditsService::class)->getBalance($agency) : 0;
    }

    public function packages()
    {
        return AiCreditPackage::active()->get();
    }

    public function ledger()
    {
        $agency = $this->agency();
        if (! $agency) {
            return collect();
        }

        return AiCreditLedger::where('agency_id', $agency->id)
            ->orderByDesc('created_at')
            ->limit(20)
            ->get();
    }

    /**
     * @return Collection<int, object{tenant_id: string|null, store_name: string, credits_consumed: int, event_count: int, last_used_at: Carbon|null}>
     */
    public function storeBreakdown(): Collection
    {
        $agency = $this->agency();
        if (! $agency) {
            return collect();
        }

        $since = match ($this->filterPeriod) {
            '30d' => now()->subDays(30),
            '90d' => now()->subDays(90),
            default => null,
        };

        return app(AiCreditsService::class)->storeBreakdown($agency, $since);
    }

    public function filterPeriodLabel(): string
    {
        return match ($this->filterPeriod) {
            '30d' => 'ultimi 30 giorni',
            '90d' => 'ultimi 90 giorni',
            default => 'tutto il periodo',
        };
    }

    public function isStripeConfigured(): bool
    {
        return ! empty(config('services.stripe.secret'));
    }

    public function packageHasStripeProduct(int $packageId): bool
    {
        return AiCreditPackage::where('id', $packageId)->whereNotNull('stripe_price_id')->exists();
    }

    /**
     * Wire:click action — crea la sessione Stripe e redirige direttamente.
     * Non viene chiamata durante il render della pagina.
     */
    public function startCheckout(int $packageId): void
    {
        $agency = $this->agency();
        $package = AiCreditPackage::find($packageId);

        if (! $agency || ! $package) {
            Notification::make()->title('Errore: dati non trovati')->danger()->send();

            return;
        }

        if (! $this->isStripeConfigured()) {
            Notification::make()
                ->title('Stripe non configurato — contatta il supporto')
                ->warning()->send();

            return;
        }

        try {
            $session = app(AiCreditsService::class)->createCheckoutSession($agency, $package);
            $this->redirect($session->url, navigate: false);
        } catch (\Throwable $e) {
            Notification::make()
                ->title('Errore Stripe: '.$e->getMessage())
                ->danger()->send();
        }
    }
}
