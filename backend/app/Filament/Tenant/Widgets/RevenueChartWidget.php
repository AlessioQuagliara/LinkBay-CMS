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

    protected function getFilters(): ?array
    {
        return [
            '7' => 'Ultimi 7 giorni',
            '30' => 'Ultimi 30 giorni',
            '90' => 'Ultimi 3 mesi',
            'year' => 'Quest\'anno',
        ];
    }

    protected function getData(): array
    {
        $filter = $this->getFilterValue('period') ?? '30';

        $days = match ($filter) {
            '7' => 6,
            '90' => 89,
            'year' => 364,
            default => 29,
        };

        $data = Order::select(
                DB::raw('DATE(created_at) as date'),
                DB::raw('SUM(total) as revenue')
            )
            ->whereBetween('created_at', [now()->subDays($days), now()])
            ->whereNotIn('status', ['cancelled', 'refunded'])
            ->groupBy('date')
            ->orderBy('date')
            ->pluck('revenue', 'date');

        $labels = [];
        $values = [];
        for ($i = $days; $i >= 0; $i--) {
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
