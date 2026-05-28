<?php

namespace App\Filament\Admin\Widgets;

use App\Models\Central\Agency;
use App\Models\Central\AiCreditLedger;
use App\Models\Central\Plan;
use App\Models\Central\Subscription;
use Filament\Widgets\StatsOverviewWidget as BaseWidget;
use Filament\Widgets\StatsOverviewWidget\Stat;

class GlobalStatsWidget extends BaseWidget
{
    protected function getStats(): array
    {
        $activeAgencies = Agency::where('status', 'active')->count();

        $mrr = Agency::active()
            ->with('plan')
            ->get()
            ->filter(fn ($a) => $a->billing_type !== 'lifetime')
            ->sum(fn ($a) => $a->plan?->price ?? 0);

        $todayPayments = AiCreditLedger::where('type', AiCreditLedger::TYPE_PURCHASE)
            ->whereDate('created_at', today())
            ->count();

        $aiSoldThisMonth = AiCreditLedger::where('type', AiCreditLedger::TYPE_PURCHASE)
            ->where('created_at', '>=', now()->startOfMonth())
            ->sum('amount');

        return [
            Stat::make('Agenzie attive', $activeAgencies)
                ->description('Status: active')
                ->color('success')
                ->icon('heroicon-o-building-office-2'),

            Stat::make('MRR', '€ ' . number_format($mrr, 2, ',', '.'))
                ->description('Monthly Recurring Revenue')
                ->color('info')
                ->icon('heroicon-o-banknotes'),

            Stat::make('Transazioni oggi', $todayPayments)
                ->description('AI credit purchases')
                ->color('primary')
                ->icon('heroicon-o-credit-card'),

            Stat::make('Crediti AI venduti (mese)', number_format($aiSoldThisMonth))
                ->description(now()->format('F Y'))
                ->color('warning')
                ->icon('heroicon-o-sparkles'),
        ];
    }
}
