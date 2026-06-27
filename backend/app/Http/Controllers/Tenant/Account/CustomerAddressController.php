<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tenant\Account;

use App\Http\Controllers\Controller;
use App\Models\Tenant\CustomerAddress;
use App\Services\Tenant\CustomerProfileService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class CustomerAddressController extends Controller
{
    public function __construct(private readonly CustomerProfileService $profileService) {}

    public function index(Request $request): JsonResponse
    {
        $addresses = $request->user('customer')->addresses()->orderByDesc('created_at')->get();

        return response()->json(['data' => $addresses]);
    }

    public function store(Request $request): JsonResponse
    {
        $validated = $request->validate($this->addressRules());

        $address = $this->profileService->addAddress($request->user('customer'), $validated);

        return response()->json([
            'data' => $address,
            'message' => 'Address added successfully.',
        ], 201);
    }

    public function update(Request $request, int $id): JsonResponse
    {
        $address = $this->findOwnedAddress($request, $id);

        $validated = $request->validate($this->addressRules(partial: true));

        $address = $this->profileService->updateAddress($address, $validated);

        return response()->json([
            'data' => $address,
            'message' => 'Address updated successfully.',
        ]);
    }

    public function destroy(Request $request, int $id): JsonResponse
    {
        $address = $this->findOwnedAddress($request, $id);

        $this->profileService->deleteAddress($address);

        return response()->json(['message' => 'Address deleted successfully.']);
    }

    public function setDefault(Request $request, int $id): JsonResponse
    {
        $validated = $request->validate([
            'type' => ['required', 'in:shipping,billing'],
        ]);

        $this->profileService->setDefaultAddress(
            $request->user('customer'),
            $id,
            $validated['type'],
        );

        return response()->json(['message' => 'Default address updated.']);
    }

    private function findOwnedAddress(Request $request, int $id): CustomerAddress
    {
        return $request->user('customer')
            ->addresses()
            ->findOrFail($id);
    }

    /** @return array<string, mixed> */
    private function addressRules(bool $partial = false): array
    {
        $required = $partial ? 'sometimes' : 'required';

        return [
            'label' => ['nullable', 'string', 'max:50'],
            'first_name' => [$required, 'string', 'max:100'],
            'last_name' => [$required, 'string', 'max:100'],
            'company' => ['nullable', 'string', 'max:150'],
            'address_line_1' => [$required, 'string', 'max:255'],
            'address_line_2' => ['nullable', 'string', 'max:255'],
            'city' => [$required, 'string', 'max:100'],
            'state' => ['nullable', 'string', 'max:100'],
            'postal_code' => [$required, 'string', 'max:20'],
            'country_code' => [$required, 'string', 'size:2'],
            'phone' => ['nullable', 'string', 'max:30'],
            'is_default_shipping' => ['boolean'],
            'is_default_billing' => ['boolean'],
        ];
    }
}
