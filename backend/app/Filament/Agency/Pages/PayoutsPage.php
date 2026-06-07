<?php

declare(strict_types=1);

namespace App\Filament\Agency\Pages;

use App\Filament\Agency\Concerns\ResolvesCurrentAgency;
use App\Models\Central\PayoutRecord;
use App\Services\StripeConnectService;
use Filament\Notifications\Notification;
use Filament\Pages\Page;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Support\Collection;

class PayoutsPage extends Page
{
    use ResolvesCurrentAgency;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-wallet';

    protected static ?string $navigationLabel = 'Payout';

    protected static ?string $slug = 'payouts';

    protected string $view = 'filament.agency.pages.payouts';

    public string $filterStatus = '';

    public string $filterDateFrom = '';

    public string $filterDateTo = '';

    public static function canAccess(): bool
    {
        $member = static::currentMemberStatic();

        return $member?->isOwnerOrAdmin() ?? false;
    }

    // ── Data methods ──────────────────────────────────────────────────────────

    /**
     * Returns payout records for the current agency, scoped by active filters.
     * Capped at 200 rows for display; exports should use buildBaseQuery() directly.
     *
     * @return Collection<int, PayoutRecord>
     */
    public function payouts(): Collection
    {
        return $this->buildBaseQuery()
            ->orderByDesc('created_at')
            ->limit(200)
            ->get();
    }

    /**
     * Aggregate totals by status for the KPI cards.
     *
     * @return array{paid_cents: int, in_transit_cents: int, pending_cents: int, failed_count: int}
     */
    public function summaryStats(): array
    {
        $agency = $this->agency();
        if (! $agency) {
            return ['paid_cents' => 0, 'in_transit_cents' => 0, 'pending_cents' => 0, 'failed_count' => 0];
        }

        $base = PayoutRecord::where('agency_id', $agency->id);

        // Apply date filters on the aggregate as well.
        if ($this->filterDateFrom !== '') {
            $base->where('created_at', '>=', $this->filterDateFrom);
        }
        if ($this->filterDateTo !== '') {
            $base->where('created_at', '<=', $this->filterDateTo.' 23:59:59');
        }

        $rows = (clone $base)
            ->selectRaw('
                status,
                COALESCE(SUM(amount_cents), 0) as total_cents,
                COUNT(*) as cnt
            ')
            ->groupBy('status')
            ->get()
            ->keyBy('status');

        return [
            'paid_cents' => (int) ($rows->get(PayoutRecord::STATUS_PAID)?->total_cents ?? 0),
            'in_transit_cents' => (int) ($rows->get(PayoutRecord::STATUS_IN_TRANSIT)?->total_cents ?? 0),
            'pending_cents' => (int) ($rows->get(PayoutRecord::STATUS_PENDING)?->total_cents ?? 0),
            'failed_count' => (int) ($rows->get(PayoutRecord::STATUS_FAILED)?->cnt ?? 0),
        ];
    }

    public function hasConnectAccount(): bool
    {
        return (bool) $this->agency()?->stripe_connect_account_id;
    }

    public function isConnectOnboarded(): bool
    {
        return (bool) $this->agency()?->stripe_connect_onboarded;
    }

    public function isStripeConfigured(): bool
    {
        return ! empty(config('services.stripe.secret'));
    }

    // ── Actions ───────────────────────────────────────────────────────────────

    /**
     * Creates a Stripe Express Dashboard login link and redirects the user.
     * Called via wire:click from the Blade.
     */
    public function openExpressDashboard(): void
    {
        $agency = $this->agency();

        if (! $agency?->stripe_connect_account_id) {
            Notification::make()->title('Stripe Connect non configurato')->warning()->send();

            return;
        }

        if (! $this->isStripeConfigured()) {
            Notification::make()->title('Stripe non configurato — contatta il supporto')->warning()->send();

            return;
        }

        try {
            $url = app(StripeConnectService::class)->createLoginLink($agency);
            $this->redirect($url, navigate: false);
        } catch (\Throwable $e) {
            Notification::make()
                ->title('Impossibile aprire il dashboard Stripe')
                ->body($e->getMessage())
                ->danger()
                ->send();
        }
    }

    // ── Internals ─────────────────────────────────────────────────────────────

    private function buildBaseQuery(): Builder
    {
        $agency = $this->agency();

        $query = PayoutRecord::where('agency_id', $agency?->id ?? 0);

        if ($this->filterStatus !== '') {
            $query->where('status', $this->filterStatus);
        }

        if ($this->filterDateFrom !== '') {
            $query->where('created_at', '>=', $this->filterDateFrom);
        }

        if ($this->filterDateTo !== '') {
            $query->where('created_at', '<=', $this->filterDateTo.' 23:59:59');
        }

        return $query;
    }
}
