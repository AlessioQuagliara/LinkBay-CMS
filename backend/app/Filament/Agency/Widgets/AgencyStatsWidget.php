<?php

namespace App\Filament\Agency\Widgets;

use App\Filament\Agency\Concerns\ResolvesCurrentAgency;
use App\Models\Central\Tenant;
use App\Services\AiCreditsService;
use Filament\Widgets\StatsOverviewWidget as BaseWidget;
use Filament\Widgets\StatsOverviewWidget\Stat;

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
        ];
    }
}
