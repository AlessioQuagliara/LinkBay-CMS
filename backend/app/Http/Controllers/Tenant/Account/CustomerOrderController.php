<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tenant\Account;

use App\Http\Controllers\Controller;
use App\Services\Tenant\CustomerProfileService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class CustomerOrderController extends Controller
{
    public function __construct(private readonly CustomerProfileService $profileService) {}

    public function index(Request $request): JsonResponse
    {
        $orders = $this->profileService->getOrderHistory(
            $request->user('customer'),
            (int) $request->input('per_page', 15),
        );

        return response()->json(['data' => $orders]);
    }

    public function show(Request $request, int $id): JsonResponse
    {
        $order = $request->user('customer')
            ->orders()
            ->with(['items.product', 'shippingMethod'])
            ->findOrFail($id);

        return response()->json(['data' => $order]);
    }
}
