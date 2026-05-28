<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tenant;

use App\Http\Controllers\Controller;
use App\Models\Tenant\DiscountCode;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Str;

class DiscountCodeController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $codes = DiscountCode::when($request->active_only, fn($q) => $q->where('is_active', true))
            ->orderBy('created_at', 'desc')
            ->paginate($request->per_page ?? 20);

        return response()->json($codes);
    }

    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'code' => 'sometimes|string|unique:discount_codes,code',
            'type' => 'required|in:percentage,fixed,free_shipping',
            'value' => 'required|numeric|min:0',
            'usage_limit' => 'nullable|integer|min:1',
            'minimum_amount' => 'nullable|numeric|min:0',
            'expires_at' => 'nullable|date|after:now',
            'is_active' => 'boolean',
            'applies_to' => 'nullable|array',
        ]);

        $validated['code'] = $validated['code'] ?? Str::upper(Str::random(8));

        $code = DiscountCode::create($validated);

        return response()->json(['data' => $code, 'message' => 'Discount code created successfully'], 201);
    }

    public function update(Request $request, DiscountCode $discountCode): JsonResponse
    {
        $validated = $request->validate([
            'type' => 'sometimes|in:percentage,fixed,free_shipping',
            'value' => 'sometimes|numeric|min:0',
            'usage_limit' => 'sometimes|nullable|integer|min:1',
            'minimum_amount' => 'sometimes|nullable|numeric|min:0',
            'expires_at' => 'sometimes|nullable|date',
            'is_active' => 'sometimes|boolean',
        ]);

        $discountCode->update($validated);

        return response()->json(['data' => $discountCode, 'message' => 'Discount code updated successfully']);
    }

    public function destroy(DiscountCode $discountCode): JsonResponse
    {
        $discountCode->delete();
        return response()->json(['message' => 'Discount code deleted successfully']);
    }
}
