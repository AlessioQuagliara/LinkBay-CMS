<?php

namespace App\Filament\Tenant\Widgets;

use App\Models\Tenant\Customer;
use App\Models\Tenant\Order;
use Filament\Widgets\StatsOverviewWidget as BaseWidget;
use Filament\Widgets\StatsOverviewWidget\Stat;

class TenantStatsOverviewWidget extends BaseWidget
{
    protected static ?int $sort = 1;

    protected function getStats(): array
    {
        $now = now();
        $start = $now->copy()->subDays(30);
        $prevStart = $now->copy()->subDays(60);
        $prevEnd = $now->copy()->subDays(30);

        $revenue = Order::whereBetween('created_at', [$start, $now])
            ->whereNotIn('status', ['cancelled', 'refunded'])
            ->sum('total');

        $prevRevenue = Order::whereBetween('created_at', [$prevStart, $prevEnd])
            ->whereNotIn('status', ['cancelled', 'refunded'])
            ->sum('total');

        $revenueTrend = $prevRevenue > 0
            ? round((($revenue - $prevRevenue) / $prevRevenue) * 100, 1)
            : 0;

        $orders = Order::whereBetween('created_at', [$start, $now])->count();
        $prevOrders = Order::whereBetween('created_at', [$prevStart, $prevEnd])->count();
        $ordersTrend = $prevOrders > 0
            ? round((($orders - $prevOrders) / $prevOrders) * 100, 1)
            : 0;

        $newCustomers = Customer::whereBetween('created_at', [$start, $now])->count();

        $pendingOrders = Order::where('status', 'pending')->count();

        return [
            Stat::make('Fatturato (30gg)', '€ ' . number_format($revenue, 2, ',', '.'))
                ->description($revenueTrend >= 0 ? "+{$revenueTrend}% vs mese prec." : "{$revenueTrend}% vs mese prec.")
                ->descriptionIcon($revenueTrend >= 0 ? 'heroicon-m-arrow-trending-up' : 'heroicon-m-arrow-trending-down')
                ->color($revenueTrend >= 0 ? 'success' : 'danger'),

            Stat::make('Ordini (30gg)', $orders)
                ->description($ordersTrend >= 0 ? "+{$ordersTrend}% vs mese prec." : "{$ordersTrend}% vs mese prec.")
                ->descriptionIcon($ordersTrend >= 0 ? 'heroicon-m-arrow-trending-up' : 'heroicon-m-arrow-trending-down')
                ->color($ordersTrend >= 0 ? 'success' : 'danger'),

            Stat::make('Nuovi clienti (30gg)', $newCustomers)
                ->description('Ultimi 30 giorni')
                ->color('info'),

            Stat::make('Ordini in attesa', $pendingOrders)
                ->description($pendingOrders > 0 ? 'Richiede attenzione' : 'Tutto ok')
                ->color($pendingOrders > 0 ? 'danger' : 'success')
                ->descriptionIcon($pendingOrders > 0 ? 'heroicon-m-exclamation-circle' : 'heroicon-m-check-circle'),
        ];
    }
}
