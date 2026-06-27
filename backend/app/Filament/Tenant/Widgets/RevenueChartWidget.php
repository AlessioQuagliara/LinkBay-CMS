<?php

declare(strict_types=1);

namespace App\Filament\Tenant\Widgets;

use App\Services\Tenant\AnalyticsService;
use Filament\Widgets\ChartWidget;
use Illuminate\Support\Carbon;
use Livewire\Attributes\On;

class RevenueChartWidget extends ChartWidget
{
    protected static ?int $sort = 2;

    protected static ?string $heading = 'Fatturato e ordini';

    protected int|string|array $columnSpan = 'full';

    protected static string $color = 'warning';

    public ?string $analyticsFrom = null;

    public ?string $analyticsTo = null;

    #[On('analyticsDateChanged')]
    public function updateDateRange(string $from, string $to): void
    {
        $this->analyticsFrom = $from;
        $this->analyticsTo = $to;
    }

    protected function getFilters(): ?array
    {
        return [
            '7' => 'Ultimi 7 giorni',
            '30' => 'Ultimi 30 giorni',
            '90' => 'Ultimi 3 mesi',
            '365' => 'Ultimi 12 mesi',
        ];
    }

    protected function getData(): array
    {
        $analytics = app(AnalyticsService::class);
        $filter = $this->getFilterValue('period') ?? '30';

        [$from, $to, $groupBy] = $this->resolvePeriod($filter);

        $revenue = $analytics->getRevenuePeriod($from, $to, $groupBy);
        $orders = $analytics->getOrdersPeriod($from, $to, $groupBy);

        $labels = $revenue->pluck('date')->all();

        return [
            'datasets' => [
                [
                    'label' => 'Fatturato (€)',
                    'data' => $revenue->pluck('revenue')->all(),
                    'borderColor' => '#f59e0b',
                    'backgroundColor' => 'rgba(245,158,11,0.15)',
                    'fill' => true,
                    'tension' => 0.4,
                    'yAxisID' => 'y',
                ],
                [
                    'label' => 'Ordini',
                    'data' => $orders->pluck('orders')->all(),
                    'borderColor' => '#6366f1',
                    'backgroundColor' => 'rgba(99,102,241,0.1)',
                    'fill' => false,
                    'tension' => 0.4,
                    'type' => 'bar',
                    'yAxisID' => 'y1',
                ],
            ],
            'labels' => $labels,
        ];
    }

    protected function getOptions(): array
    {
        return [
            'scales' => [
                'y' => [
                    'position' => 'left',
                    'ticks' => ['callback' => 'function(v) { return "€" + v; }'],
                ],
                'y1' => [
                    'position' => 'right',
                    'grid' => ['drawOnChartArea' => false],
                ],
            ],
        ];
    }

    protected function getType(): string
    {
        return 'line';
    }

    /** @return array{0: Carbon, 1: Carbon, 2: string} */
    private function resolvePeriod(string $filter): array
    {
        if ($this->analyticsFrom && $this->analyticsTo) {
            $from = Carbon::parse($this->analyticsFrom);
            $to = Carbon::parse($this->analyticsTo);
            $days = $from->diffInDays($to);
            $groupBy = $days > 90 ? 'month' : ($days > 14 ? 'week' : 'day');

            return [$from, $to, $groupBy];
        }

        $days = $filter === '365' ? 364 : (int) $filter - 1;
        $from = now()->subDays($days)->startOfDay();
        $to = now()->endOfDay();
        $groupBy = $days >= 90 ? 'month' : ($days >= 14 ? 'week' : 'day');

        return [$from, $to, $groupBy];
    }
}
