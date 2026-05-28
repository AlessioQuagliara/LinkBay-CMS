<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tenant;

use App\Http\Controllers\Controller;
use App\Models\Tenant\Order;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class OrderController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $orders = Order::with(['customer', 'items', 'shippingMethod'])
            ->when($request->status, fn($q) => $q->where('status', $request->status))
            ->when($request->customer_id, fn($q) => $q->where('customer_id', $request->customer_id))
            ->when($request->from, fn($q) => $q->where('created_at', '>=', $request->from))
            ->when($request->to, fn($q) => $q->where('created_at', '<=', $request->to))
            ->orderBy('created_at', 'desc')
            ->paginate($request->per_page ?? 20);

        return response()->json($orders);
    }

    public function show(Order $order): JsonResponse
    {
        return response()->json(['data' => $order->load(['customer', 'items.product', 'shippingMethod', 'discountCode'])]);
    }

    public function updateStatus(Request $request, Order $order): JsonResponse
    {
        $validated = $request->validate([
            'status' => 'required|in:pending,confirmed,processing,shipped,delivered,cancelled,refunded',
            'tracking_number' => 'nullable|string',
            'notes' => 'nullable|string',
        ]);

        $order->update($validated);

        return response()->json(['data' => $order, 'message' => 'Order status updated']);
    }
}
