<?php

declare(strict_types=1);

namespace App\Http\Controllers\Central;

use App\Http\Controllers\Controller;
use App\Models\Central\Tenant;
use App\Services\TenantProvisioningService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;
use Illuminate\Validation\ValidationException;

class TenantController extends Controller
{
    public function __construct(
        private readonly TenantProvisioningService $provisioningService
    ) {}

    public function index(Request $request): JsonResponse
    {
        $tenants = Tenant::with(['plan', 'subscription'])
            ->when($request->search, fn($q) => $q->where('name', 'like', "%{$request->search}%"))
            ->when($request->status, fn($q) => $q->where('status', $request->status))
            ->latest()
            ->paginate($request->per_page ?? 15);

        return response()->json($tenants);
    }

    public function show(string $id): JsonResponse
    {
        $tenant = Tenant::with(['plan', 'subscription'])->findOrFail($id);
        return response()->json(['data' => $tenant]);
    }

    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'name' => 'required|string|max:255',
            'domain' => 'required|string|max:255|unique:tenants,id',
            'plan_id' => 'nullable|exists:plans,id',
            'admin_email' => 'required|email',
            'admin_password' => 'required|string|min:8',
        ]);

        $tenant = $this->provisioningService->provision($validated);

        return response()->json(['data' => $tenant, 'message' => 'Tenant provisioned successfully'], 201);
    }

    public function update(Request $request, string $id): JsonResponse
    {
        $tenant = Tenant::findOrFail($id);

        $validated = $request->validate([
            'name' => 'sometimes|string|max:255',
            'status' => 'sometimes|in:active,suspended,cancelled',
            'plan_id' => 'sometimes|nullable|exists:plans,id',
        ]);

        $tenant->update($validated);

        return response()->json(['data' => $tenant, 'message' => 'Tenant updated successfully']);
    }

    public function destroy(string $id): JsonResponse
    {
        $tenant = Tenant::findOrFail($id);
        $this->provisioningService->deprovision($tenant);

        return response()->json(['message' => 'Tenant deprovisioned successfully']);
    }
}
