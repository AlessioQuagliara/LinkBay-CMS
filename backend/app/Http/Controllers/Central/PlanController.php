<?php

declare(strict_types=1);

namespace App\Http\Controllers\Central;

use App\Http\Controllers\Controller;
use App\Models\Central\Plan;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class PlanController extends Controller
{
    public function index(): JsonResponse
    {
        $plans = Plan::where('is_active', true)->orderBy('sort_order')->get();
        return response()->json(['data' => $plans]);
    }

    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'slug' => 'required|string|unique:plans,slug',
            'price' => 'required|numeric|min:0',
            'billing_interval' => 'required|in:month,year',
            'features' => 'nullable|array',
            'limits' => 'nullable|array',
            'stripe_price_id' => 'nullable|string',
            'is_active' => 'boolean',
            'sort_order' => 'integer',
        ]);

        $plan = Plan::create($validated);

        return response()->json(['data' => $plan, 'message' => 'Plan created successfully'], 201);
    }

    public function show(Plan $plan): JsonResponse
    {
        return response()->json(['data' => $plan->load('tenants')]);
    }

    public function update(Request $request, Plan $plan): JsonResponse
    {
        $validated = $request->validate([
            'name' => 'sometimes|string|max:255',
            'price' => 'sometimes|numeric|min:0',
            'features' => 'sometimes|nullable|array',
            'limits' => 'sometimes|nullable|array',
            'is_active' => 'sometimes|boolean',
        ]);

        $plan->update($validated);

        return response()->json(['data' => $plan, 'message' => 'Plan updated successfully']);
    }

    public function destroy(Plan $plan): JsonResponse
    {
        if ($plan->tenants()->exists()) {
            return response()->json(['message' => 'Cannot delete plan with active tenants'], 422);
        }

        $plan->delete();

        return response()->json(['message' => 'Plan deleted successfully']);
    }
}
