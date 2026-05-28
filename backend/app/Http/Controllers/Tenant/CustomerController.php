<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tenant;

use App\Http\Controllers\Controller;
use App\Models\Tenant\Customer;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class CustomerController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $customers = Customer::withCount('orders')
            ->when($request->search, fn($q) => $q
                ->where('name', 'like', "%{$request->search}%")
                ->orWhere('email', 'like', "%{$request->search}%")
            )
            ->orderBy('created_at', 'desc')
            ->paginate($request->per_page ?? 20);

        return response()->json($customers);
    }

    public function show(Customer $customer): JsonResponse
    {
        return response()->json(['data' => $customer->load('orders')]);
    }

    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'email' => 'required|email|unique:customers,email',
            'phone' => 'nullable|string|max:30',
            'address' => 'nullable|array',
            'notes' => 'nullable|string',
            'tags' => 'nullable|array',
        ]);

        $customer = Customer::create($validated);

        return response()->json(['data' => $customer, 'message' => 'Customer created successfully'], 201);
    }

    public function update(Request $request, Customer $customer): JsonResponse
    {
        $validated = $request->validate([
            'name' => 'sometimes|string|max:255',
            'email' => "sometimes|email|unique:customers,email,{$customer->id}",
            'phone' => 'sometimes|nullable|string|max:30',
            'address' => 'sometimes|nullable|array',
            'notes' => 'sometimes|nullable|string',
            'tags' => 'sometimes|nullable|array',
        ]);

        $customer->update($validated);

        return response()->json(['data' => $customer, 'message' => 'Customer updated successfully']);
    }

    public function destroy(Customer $customer): JsonResponse
    {
        $customer->delete();
        return response()->json(['message' => 'Customer deleted successfully']);
    }
}
