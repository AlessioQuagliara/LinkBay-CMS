<?php

declare(strict_types=1);

namespace App\Services\Tenant;

use App\Models\Tenant\Customer;
use App\Models\Tenant\CustomerAddress;
use Illuminate\Contracts\Pagination\LengthAwarePaginator;
use Illuminate\Database\Eloquent\Collection;
use Illuminate\Validation\ValidationException;

class CustomerProfileService
{
    public function updateProfile(Customer $customer, array $data): Customer
    {
        $customer->update(array_filter([
            'name' => $data['name'] ?? null,
            'phone' => $data['phone'] ?? null,
            'accepts_marketing' => $data['accepts_marketing'] ?? null,
        ], fn ($value) => $value !== null));

        return $customer->fresh();
    }

    public function addAddress(Customer $customer, array $data): CustomerAddress
    {
        $address = $customer->addresses()->create($data);

        if ($address->is_default_shipping) {
            $this->clearDefaultShipping($customer, $address->id);
            $customer->update(['default_shipping_address_id' => $address->id]);
        }

        if ($address->is_default_billing) {
            $this->clearDefaultBilling($customer, $address->id);
            $customer->update(['default_billing_address_id' => $address->id]);
        }

        return $address;
    }

    public function updateAddress(CustomerAddress $address, array $data): CustomerAddress
    {
        $customer = $address->customer;

        $address->update($data);

        if ($address->is_default_shipping) {
            $this->clearDefaultShipping($customer, $address->id);
            $customer->update(['default_shipping_address_id' => $address->id]);
        }

        if ($address->is_default_billing) {
            $this->clearDefaultBilling($customer, $address->id);
            $customer->update(['default_billing_address_id' => $address->id]);
        }

        return $address->fresh();
    }

    public function deleteAddress(CustomerAddress $address): void
    {
        $customer = $address->customer;

        if ((int) $customer->default_shipping_address_id === $address->id) {
            $customer->update(['default_shipping_address_id' => null]);
        }

        if ((int) $customer->default_billing_address_id === $address->id) {
            $customer->update(['default_billing_address_id' => null]);
        }

        $address->delete();
    }

    /**
     * @param  'shipping'|'billing'  $type
     *
     * @throws ValidationException if the address does not belong to the customer
     */
    public function setDefaultAddress(Customer $customer, int $addressId, string $type): void
    {
        $address = $customer->addresses()->find($addressId);

        if (! $address) {
            throw ValidationException::withMessages([
                'address_id' => ['Address not found.'],
            ]);
        }

        if ($type === 'shipping') {
            $this->clearDefaultShipping($customer, $addressId);
            $address->update(['is_default_shipping' => true]);
            $customer->update(['default_shipping_address_id' => $addressId]);
        } else {
            $this->clearDefaultBilling($customer, $addressId);
            $address->update(['is_default_billing' => true]);
            $customer->update(['default_billing_address_id' => $addressId]);
        }
    }

    public function getOrderHistory(Customer $customer, int $perPage = 15): LengthAwarePaginator
    {
        return $customer->orders()
            ->with('items.product')
            ->orderByDesc('created_at')
            ->paginate($perPage);
    }

    public function addToWishlist(Customer $customer, int $productId): void
    {
        $customer->wishlistProducts()->syncWithoutDetaching([$productId]);
    }

    public function removeFromWishlist(Customer $customer, int $productId): void
    {
        $customer->wishlistProducts()->detach($productId);
    }

    public function getWishlist(Customer $customer): Collection
    {
        return $customer->wishlistProducts()->get();
    }

    private function clearDefaultShipping(Customer $customer, int $exceptAddressId): void
    {
        $customer->addresses()
            ->where('id', '!=', $exceptAddressId)
            ->where('is_default_shipping', true)
            ->update(['is_default_shipping' => false]);
    }

    private function clearDefaultBilling(Customer $customer, int $exceptAddressId): void
    {
        $customer->addresses()
            ->where('id', '!=', $exceptAddressId)
            ->where('is_default_billing', true)
            ->update(['is_default_billing' => false]);
    }
}
