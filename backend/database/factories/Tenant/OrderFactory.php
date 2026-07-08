<?php

declare(strict_types=1);

namespace Database\Factories\Tenant;

use App\Models\Tenant\Customer;
use App\Models\Tenant\Order;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends Factory<Order>
 */
class OrderFactory extends Factory
{
    protected $model = Order::class;

    public function definition(): array
    {
        return [
            'customer_id' => Customer::factory(),
            'status' => Order::STATUS_PENDING,
            'total' => 100,
            'subtotal' => 100,
            'discount_total' => 0,
            'shipping_total' => 0,
            'payment_method' => 'card',
            'payment_status' => Order::PAYMENT_STATUS_PENDING,
        ];
    }

    public function paid(): static
    {
        return $this->state(fn (array $attributes) => [
            'payment_status' => Order::PAYMENT_STATUS_PAID,
            'status' => Order::STATUS_CONFIRMED,
        ]);
    }
}
