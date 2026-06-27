<?php

declare(strict_types=1);

namespace App\Filament\Tenant\Widgets;

use App\Services\Tenant\AnalyticsService;
use Filament\Widgets\StatsOverviewWidget as BaseWidget;
use Filament\Widgets\StatsOverviewWidget\Stat;
use Illuminate\Support\Carbon;
use Livewire\Attributes\On;

class TenantStatsOverviewWidget extends BaseWidget
{
    protected static ?int $sort = 1;

    protected static ?string $pollingInterval = '60s';

    public ?string $analyticsFrom = null;

    public ?string $analyticsTo = null;

    #[On('analyticsDateChanged')]
    public function updateDateRange(string $from, string $to): void
    {
        $this->analyticsFrom = $from;
        $this->analyticsTo = $to;
    }

    protected function getStats(): array
    {
        $analytics = app(AnalyticsService::class);

        [$from, $to] = $this->resolveRange();

        $revenue = $analytics->compareWithPreviousPeriod('getRevenueTotal', $from, $to);
        $orders = $analytics->compareWithPreviousPeriod('getOrdersCount', $from, $to);
        $aov = $analytics->compareWithPreviousPeriod('getAverageOrderValue', $from, $to);
        $customers = $analytics->compareWithPreviousPeriod('getNewCustomersCount', $from, $to);

        return [
            Stat::make('Fatturato', '€ '.number_format((float) $revenue['current'], 2, ',', '.'))
                ->description($this->trendLabel($revenue))
                ->descriptionIcon($revenue['trend'] === 'up' ? 'heroicon-m-arrow-trending-up' : 'heroicon-m-arrow-trending-down')
                ->color($revenue['trend'] === 'up' ? 'success' : 'danger')
                ->chart($this->sparkline($analytics, $from, $to)),

            Stat::make('Ordini', (string) (int) $orders['current'])
                ->description($this->trendLabel($orders))
                ->descriptionIcon($orders['trend'] === 'up' ? 'heroicon-m-arrow-trending-up' : 'heroicon-m-arrow-trending-down')
                ->color($orders['trend'] === 'up' ? 'success' : 'danger'),

            Stat::make('Valore medio ordine', '€ '.number_format((float) $aov['current'], 2, ',', '.'))
                ->description($this->trendLabel($aov))
                ->descriptionIcon($aov['trend'] === 'up' ? 'heroicon-m-arrow-trending-up' : 'heroicon-m-arrow-trending-down')
                ->color($aov['trend'] === 'up' ? 'success' : 'warning'),

            Stat::make('Nuovi clienti', (string) (int) $customers['current'])
                ->description($this->trendLabel($customers))
                ->descriptionIcon($customers['trend'] === 'up' ? 'heroicon-m-arrow-trending-up' : 'heroicon-m-arrow-trending-down')
                ->color('info'),
        ];
    }

    /** @param  array{change_percent: float, trend: string}  $comparison */
    private function trendLabel(array $comparison): string
    {
        $pct = abs($comparison['change_percent']);
        $prefix = $comparison['trend'] === 'up' ? '+' : ($comparison['trend'] === 'down' ? '-' : '');

        return "{$prefix}{$pct}% vs periodo prec.";
    }

    /** @return array<int, float> */
    private function sparkline(AnalyticsService $analytics, Carbon $from, Carbon $to): array
    {
        $sparkFrom = now()->subDays(6)->startOfDay();
        $sparkTo = now()->endOfDay();

        return $analytics->getRevenuePeriod($sparkFrom, $sparkTo, 'day')
            ->pluck('revenue')
            ->map(fn ($v) => (float) $v)
            ->values()
            ->all();
    }

    /** @return array{0: Carbon, 1: Carbon} */
    private function resolveRange(): array
    {
        if ($this->analyticsFrom && $this->analyticsTo) {
            return [Carbon::parse($this->analyticsFrom), Carbon::parse($this->analyticsTo)];
        }

        return [now()->subDays(29)->startOfDay(), now()->endOfDay()];
    }
}
