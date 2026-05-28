<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tenant;

use App\Http\Controllers\Controller;
use App\Models\Tenant\Customer;
use App\Models\Tenant\Order;
use App\Models\Tenant\Product;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;

class AnalyticsController extends Controller
{
    public function summary(Request $request): JsonResponse
    {
        $from = $request->from ? now()->parse($request->from) : now()->subDays(30);
        $to = $request->to ? now()->parse($request->to) : now();

        $revenue = Order::whereBetween('created_at', [$from, $to])
            ->whereNotIn('status', ['cancelled', 'refunded'])
            ->sum('total');

        $ordersCount = Order::whereBetween('created_at', [$from, $to])->count();

        $newCustomers = Customer::whereBetween('created_at', [$from, $to])->count();

        $avgOrderValue = $ordersCount > 0 ? $revenue / $ordersCount : 0;

        $topProducts = Product::select('products.id', 'products.name', DB::raw('SUM(order_items.quantity) as sold_qty'), DB::raw('SUM(order_items.total) as revenue'))
            ->join('order_items', 'products.id', '=', 'order_items.product_id')
            ->join('orders', 'order_items.order_id', '=', 'orders.id')
            ->whereBetween('orders.created_at', [$from, $to])
            ->groupBy('products.id', 'products.name')
            ->orderByDesc('revenue')
            ->limit(5)
            ->get();

        $ordersByStatus = Order::whereBetween('created_at', [$from, $to])
            ->selectRaw('status, COUNT(*) as count')
            ->groupBy('status')
            ->pluck('count', 'status');

        return response()->json([
            'data' => [
                'period' => ['from' => $from->toDateString(), 'to' => $to->toDateString()],
                'revenue' => round((float) $revenue, 2),
                'orders_count' => $ordersCount,
                'new_customers' => $newCustomers,
                'avg_order_value' => round($avgOrderValue, 2),
                'top_products' => $topProducts,
                'orders_by_status' => $ordersByStatus,
            ],
        ]);
    }
}
