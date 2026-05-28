<?php

namespace App\Filament\Admin\Widgets;

use App\Models\Central\Plan;
use App\Models\Central\Subscription;
use App\Models\Central\Tenant;
use Filament\Widgets\StatsOverviewWidget as BaseWidget;
use Filament\Widgets\StatsOverviewWidget\Stat;

class AdminStatsOverviewWidget extends BaseWidget
{
    protected function getStats(): array
    {
        $activeTenants = Tenant::where('status', 'active')->count();

        $mrr = Subscription::whereHas('plan')
            ->where('status', 'active')
            ->join('plans', 'subscriptions.plan_id', '=', 'plans.id')
            ->sum('plans.price');

        $newThisMonth = Tenant::where('created_at', '>=', now()->startOfMonth())->count();

        $freeTenants = Tenant::whereHas('plan', fn ($q) => $q->where('price', 0))
            ->orWhereNull('plan_id')
            ->where('status', 'active')
            ->count();

        return [
            Stat::make('Tenant attivi', $activeTenants)
                ->description('Totale tenant con status active')
                ->color('success')
                ->icon('heroicon-o-building-office-2'),

            Stat::make('MRR', '€ ' . number_format($mrr, 2, ',', '.'))
                ->description('Monthly Recurring Revenue')
                ->color('info')
                ->icon('heroicon-o-banknotes'),

            Stat::make('Nuovi (questo mese)', $newThisMonth)
                ->description(now()->format('F Y'))
                ->color('primary')
                ->icon('heroicon-o-user-plus'),

            Stat::make('Free / senza piano', $freeTenants)
                ->description('Da convertire')
                ->color('warning')
                ->icon('heroicon-o-gift'),
        ];
    }
}
