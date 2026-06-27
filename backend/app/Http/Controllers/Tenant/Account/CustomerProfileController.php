<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tenant\Account;

use App\Http\Controllers\Controller;
use App\Services\Tenant\CustomerProfileService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class CustomerProfileController extends Controller
{
    public function __construct(private readonly CustomerProfileService $profileService) {}

    public function show(Request $request): JsonResponse
    {
        $customer = $request->user('customer');

        return response()->json([
            'data' => $customer->load(['defaultShippingAddress', 'defaultBillingAddress']),
        ]);
    }

    public function update(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'name' => ['sometimes', 'string', 'max:255'],
            'phone' => ['sometimes', 'nullable', 'string', 'max:30'],
            'accepts_marketing' => ['sometimes', 'boolean'],
        ]);

        $customer = $this->profileService->updateProfile(
            $request->user('customer'),
            $validated,
        );

        return response()->json([
            'data' => $customer,
            'message' => 'Profile updated successfully.',
        ]);
    }
}
