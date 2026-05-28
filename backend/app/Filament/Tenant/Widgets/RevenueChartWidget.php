<?php

namespace App\Filament\Tenant\Widgets;

use App\Models\Tenant\Order;
use Filament\Widgets\ChartWidget;
use Illuminate\Support\Facades\DB;

class RevenueChartWidget extends ChartWidget
{
    protected static ?string $heading = 'Fatturato — ultimi 30 giorni';
    protected static ?int $sort = 2;
    protected int|string|array $columnSpan = 'full';
    protected static string $color = 'warning';

    protected function getData(): array
    {
        $data = Order::select(
                DB::raw('DATE(created_at) as date'),
                DB::raw('SUM(total) as revenue')
            )
            ->whereBetween('created_at', [now()->subDays(29), now()])
            ->whereNotIn('status', ['cancelled', 'refunded'])
            ->groupBy('date')
            ->orderBy('date')
            ->pluck('revenue', 'date');

        $labels = [];
        $values = [];
        for ($i = 29; $i >= 0; $i--) {
            $date = now()->subDays($i)->format('Y-m-d');
            $labels[] = now()->subDays($i)->format('d/m');
            $values[] = round((float) ($data[$date] ?? 0), 2);
        }

        return [
            'datasets' => [
                [
                    'label' => 'Fatturato (€)',
                    'data' => $values,
                    'borderColor' => '#f59e0b',
                    'backgroundColor' => 'rgba(245,158,11,0.15)',
                    'fill' => true,
                    'tension' => 0.4,
                ],
            ],
            'labels' => $labels,
        ];
    }

    protected function getType(): string
    {
        return 'line';
    }
}
