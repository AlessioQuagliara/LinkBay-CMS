<?php

namespace App\Filament\Agency\Widgets;

use App\Filament\Agency\Concerns\ResolvesCurrentAgency;
use App\Models\Central\CommissionRecord;
use App\Models\Central\Tenant;
use App\Services\AiCreditsService;
use Filament\Widgets\StatsOverviewWidget as BaseWidget;
use Filament\Widgets\StatsOverviewWidget\Stat;
use Illuminate\Support\Carbon;

class AgencyStatsWidget extends BaseWidget
{
    use ResolvesCurrentAgency;

    protected function getStats(): array
    {
        $agency = $this->agency();

        $storeCount = $agency
            ? Tenant::where('agency_id', $agency->id)->where('status', 'active')->count()
            : 0;

        $aiBalance = $agency
            ? app(AiCreditsService::class)->getBalance($agency)
            : 0;

        $planName = $agency?->plan?->name ?? 'Nessun piano';

        $maxStores = $agency?->plan?->limits['max_stores'] ?? null;
        $storeDesc = $maxStores !== null
            ? "di {$maxStores} disponibili"
            : 'illimitati';

        $revenue = $agency ? $this->monthlyRevenue($agency->id) : ['net' => 0, 'gross' => 0, 'count' => 0];

        $revenueDesc = $revenue['count'] > 0
            ? 'GMV €'.number_format($revenue['gross'] / 100, 2, ',', '.').' · '.$revenue['count'].($revenue['count'] === 1 ? ' transazione' : ' transazioni')
            : 'mese corrente';

        return [
            Stat::make('Piano attuale', $planName)
                ->description($agency?->billing_type === 'lifetime' ? 'Lifetime (AppSumo)' : 'Abbonamento')
                ->color($agency?->plan ? 'success' : 'warning')
                ->icon('heroicon-o-credit-card'),

            Stat::make('Negozi attivi', $storeCount)
                ->description($storeDesc)
                ->color('primary')
                ->icon('heroicon-o-shopping-bag'),

            Stat::make('Crediti AI', number_format($aiBalance))
                ->description('Saldo disponibile')
                ->color($aiBalance > 0 ? 'info' : 'danger')
                ->icon('heroicon-o-sparkles'),

            Stat::make('Ricavi netti', '€'.number_format($revenue['net'] / 100, 2, ',', '.'))
                ->description($revenueDesc)
                ->color($revenue['net'] > 0 ? 'success' : 'gray')
                ->icon('heroicon-o-banknotes'),
        ];
    }

    /**
     * Sums settled CommissionRecord amounts for the current calendar month.
     *
     * @return array{net: int, gross: int, count: int} values in cents
     */
    public function monthlyRevenue(int $agencyId, ?Carbon $forMonth = null): array
    {
        $month = $forMonth ?? now();

        $row = CommissionRecord::where('agency_id', $agencyId)
            ->where('status', CommissionRecord::STATUS_SETTLED)
            ->whereNotNull('settled_at')
            ->whereYear('settled_at', $month->year)
            ->whereMonth('settled_at', $month->month)
            ->selectRaw('COALESCE(SUM(gross_amount_cents), 0) as total_gross, COALESCE(SUM(net_to_agency_cents), 0) as total_net, COUNT(*) as total_count')
            ->first();

        return [
            'net' => (int) ($row?->total_net ?? 0),
            'gross' => (int) ($row?->total_gross ?? 0),
            'count' => (int) ($row?->total_count ?? 0),
        ];
    }
}
