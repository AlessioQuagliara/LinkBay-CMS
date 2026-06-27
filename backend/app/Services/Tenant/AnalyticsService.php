<?php

declare(strict_types=1);

namespace App\Services\Tenant;

use Carbon\Carbon;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\DB;

class AnalyticsService
{
    private function tenantId(): string
    {
        try {
            return (string) (tenancy()->tenant?->id ?? 'global');
        } catch (\Throwable) {
            return 'global';
        }
    }

    /**
     * @template T
     *
     * @param  callable(): T  $callback
     * @return T
     */
    private function remember(string $metric, Carbon $from, Carbon $to, callable $callback): mixed
    {
        $key = "analytics:{$this->tenantId()}:{$metric}:{$from->toDateString()}:{$to->toDateString()}";

        return Cache::remember($key, now()->addMinutes(15), $callback);
    }

    public function flushCache(): void
    {
        try {
            Cache::tags(["analytics:{$this->tenantId()}"])->flush();
        } catch (\Throwable) {
            // Cache driver doesn't support tags — no-op, TTL will expire naturally
        }
    }

    // ─── Revenue ─────────────────────────────────────────────────────────────

    public function getRevenueTotal(Carbon $from, Carbon $to): float
    {
        return (float) $this->remember("revenue_total", $from, $to, fn () => DB::table('orders')
            ->whereBetween('created_at', [$from->startOfDay(), $to->endOfDay()])
            ->whereNotIn('status', ['cancelled', 'refunded'])
            ->sum('total'));
    }

    /**
     * @return Collection<int, array{date: string, revenue: float}>
     */
    public function getRevenuePeriod(Carbon $from, Carbon $to, string $groupBy = 'day'): Collection
    {
        return $this->remember("revenue_period_{$groupBy}", $from, $to, function () use ($from, $to, $groupBy) {
            $dateExpr = $this->dateExpression($groupBy);

            $rows = DB::table('orders')
                ->selectRaw("{$dateExpr} as date, SUM(total) as revenue")
                ->whereBetween('created_at', [$from->startOfDay(), $to->endOfDay()])
                ->whereNotIn('status', ['cancelled', 'refunded'])
                ->groupByRaw($dateExpr)
                ->orderByRaw($dateExpr)
                ->get()
                ->keyBy('date');

            return $this->fillDateSeries($from, $to, $groupBy, $rows, fn ($row) => [
                'date' => $row ? $row->date : '',
                'revenue' => $row ? round((float) $row->revenue, 2) : 0.0,
            ]);
        });
    }

    public function getOrdersCount(Carbon $from, Carbon $to): int
    {
        return (int) $this->remember("orders_count", $from, $to, fn () => DB::table('orders')
            ->whereBetween('created_at', [$from->startOfDay(), $to->endOfDay()])
            ->count());
    }

    /**
     * @return Collection<int, array{date: string, orders: int}>
     */
    public function getOrdersPeriod(Carbon $from, Carbon $to, string $groupBy = 'day'): Collection
    {
        return $this->remember("orders_period_{$groupBy}", $from, $to, function () use ($from, $to, $groupBy) {
            $dateExpr = $this->dateExpression($groupBy);

            $rows = DB::table('orders')
                ->selectRaw("{$dateExpr} as date, COUNT(*) as orders")
                ->whereBetween('created_at', [$from->startOfDay(), $to->endOfDay()])
                ->groupByRaw($dateExpr)
                ->orderByRaw($dateExpr)
                ->get()
                ->keyBy('date');

            return $this->fillDateSeries($from, $to, $groupBy, $rows, fn ($row) => [
                'date' => $row ? $row->date : '',
                'orders' => $row ? (int) $row->orders : 0,
            ]);
        });
    }

    public function getAverageOrderValue(Carbon $from, Carbon $to): float
    {
        return (float) $this->remember("avg_order_value", $from, $to, function () use ($from, $to) {
            $result = DB::table('orders')
                ->whereBetween('created_at', [$from->startOfDay(), $to->endOfDay()])
                ->whereNotIn('status', ['cancelled', 'refunded'])
                ->selectRaw('AVG(total) as avg_value')
                ->value('avg_value');

            return round((float) $result, 2);
        });
    }

    // ─── Clienti ─────────────────────────────────────────────────────────────

    public function getNewCustomersCount(Carbon $from, Carbon $to): int
    {
        return (int) $this->remember("new_customers", $from, $to, fn () => DB::table('customers')
            ->whereBetween('created_at', [$from->startOfDay(), $to->endOfDay()])
            ->count());
    }

    public function getReturningCustomersRate(Carbon $from, Carbon $to): float
    {
        return (float) $this->remember("returning_rate", $from, $to, function () use ($from, $to) {
            $total = DB::table('orders')
                ->whereBetween('created_at', [$from->startOfDay(), $to->endOfDay()])
                ->whereNotNull('customer_id')
                ->distinct('customer_id')
                ->count('customer_id');

            if ($total === 0) {
                return 0.0;
            }

            // Customers with more than one order in the period
            $returning = DB::table('orders')
                ->selectRaw('customer_id, COUNT(*) as order_count')
                ->whereBetween('created_at', [$from->startOfDay(), $to->endOfDay()])
                ->whereNotNull('customer_id')
                ->groupBy('customer_id')
                ->havingRaw('COUNT(*) > 1')
                ->get()
                ->count();

            return round(($returning / $total) * 100, 1);
        });
    }

    // ─── Prodotti ─────────────────────────────────────────────────────────────

    /**
     * @return Collection<int, array{product_id: int, product_name: string, units_sold: int, revenue: float}>
     */
    public function getTopProducts(Carbon $from, Carbon $to, int $limit = 10): Collection
    {
        return $this->remember("top_products_{$limit}", $from, $to, fn () => DB::table('order_items')
            ->join('orders', 'order_items.order_id', '=', 'orders.id')
            ->join('products', 'order_items.product_id', '=', 'products.id')
            ->selectRaw('
                order_items.product_id,
                products.name as product_name,
                products.sku,
                SUM(order_items.quantity) as units_sold,
                SUM(order_items.total) as revenue
            ')
            ->whereBetween('orders.created_at', [$from->startOfDay(), $to->endOfDay()])
            ->whereNotIn('orders.status', ['cancelled', 'refunded'])
            ->groupBy('order_items.product_id', 'products.name', 'products.sku')
            ->orderByDesc('revenue')
            ->limit($limit)
            ->get()
            ->map(fn ($row) => [
                'product_id' => $row->product_id,
                'product_name' => $row->product_name,
                'sku' => $row->sku,
                'units_sold' => (int) $row->units_sold,
                'revenue' => round((float) $row->revenue, 2),
            ]));
    }

    public function getLowStockProducts(int $threshold = 5): Collection
    {
        return DB::table('products')
            ->select('id', 'name', 'sku', 'stock', 'quantity')
            ->where('is_active', true)
            ->where('track_quantity', true)
            ->where('stock', '<=', $threshold)
            ->where('stock', '>', 0)
            ->orderBy('stock')
            ->get();
    }

    public function getOutOfStockProducts(): Collection
    {
        return DB::table('products')
            ->select('id', 'name', 'sku', 'stock')
            ->where('is_active', true)
            ->where('track_quantity', true)
            ->where('stock', '<=', 0)
            ->orderBy('name')
            ->get();
    }

    // ─── Conversione ─────────────────────────────────────────────────────────

    public function getCartAbandonmentRate(Carbon $from, Carbon $to): float
    {
        return (float) $this->remember("cart_abandonment", $from, $to, function () use ($from, $to) {
            $total = DB::table('checkout_sessions')
                ->whereBetween('created_at', [$from->startOfDay(), $to->endOfDay()])
                ->count();

            if ($total === 0) {
                return 0.0;
            }

            $abandoned = DB::table('checkout_sessions')
                ->whereBetween('created_at', [$from->startOfDay(), $to->endOfDay()])
                ->where('status', 'abandoned')
                ->count();

            return round(($abandoned / $total) * 100, 1);
        });
    }

    // ─── Confronto periodo ────────────────────────────────────────────────────

    /**
     * @return array{current: float|int, previous: float|int, change_percent: float, trend: 'up'|'down'|'flat'}
     */
    public function compareWithPreviousPeriod(string $metric, Carbon $from, Carbon $to): array
    {
        $diffDays = (int) $from->diffInDays($to);
        $prevTo = $from->copy()->subDay();
        $prevFrom = $prevTo->copy()->subDays($diffDays);

        $current = $this->$metric($from, $to);
        $previous = $this->$metric($prevFrom, $prevTo);

        $changePercent = 0.0;
        if ($previous > 0) {
            $changePercent = round((($current - $previous) / $previous) * 100, 1);
        } elseif ($current > 0) {
            $changePercent = 100.0;
        }

        return [
            'current' => $current,
            'previous' => $previous,
            'change_percent' => $changePercent,
            'trend' => match (true) {
                $changePercent > 0 => 'up',
                $changePercent < 0 => 'down',
                default => 'flat',
            },
        ];
    }

    // ─── Helpers ─────────────────────────────────────────────────────────────

    private function dateExpression(string $groupBy): string
    {
        $driver = DB::getDriverName();

        return match ($groupBy) {
            'month' => $driver === 'pgsql'
                ? "TO_CHAR(created_at, 'YYYY-MM')"
                : "DATE_FORMAT(created_at, '%Y-%m')",
            'week' => $driver === 'pgsql'
                ? "TO_CHAR(DATE_TRUNC('week', created_at), 'YYYY-MM-DD')"
                : "DATE_FORMAT(created_at, '%Y-%u')",
            default => 'DATE(created_at)',
        };
    }

    /**
     * Build a complete date series filling gaps with default values.
     *
     * @param  \Illuminate\Support\Collection<string, mixed>  $rows
     * @param  callable(object|null): array<string, mixed>  $transform
     * @return Collection<int, array<string, mixed>>
     */
    private function fillDateSeries(Carbon $from, Carbon $to, string $groupBy, Collection $rows, callable $transform): Collection
    {
        $result = collect();
        $current = $from->copy()->startOfDay();

        $step = match ($groupBy) {
            'month' => 'addMonth',
            'week' => 'addWeek',
            default => 'addDay',
        };

        while ($current->lte($to)) {
            $key = match ($groupBy) {
                'month' => $current->format('Y-m'),
                'week' => $current->copy()->startOfWeek()->format('Y-m-d'),
                default => $current->format('Y-m-d'),
            };

            $row = $rows->get($key);
            $entry = $transform($row);
            $entry['date'] = $key;
            $result->push($entry);

            $current->$step();
        }

        return $result;
    }
}
