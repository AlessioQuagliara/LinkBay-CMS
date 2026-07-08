<?php

declare(strict_types=1);

namespace Database\Factories\Tenant;

use App\Models\Tenant\CartSession;
use App\Models\Tenant\CheckoutSession;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends Factory<CheckoutSession>
 */
class CheckoutSessionFactory extends Factory
{
    protected $model = CheckoutSession::class;

    public function definition(): array
    {
        return [
            'cart_session_id' => CartSession::factory(),
            'status' => CheckoutSession::STATUS_PENDING,
            'shipping_address' => [
                'first_name' => fake()->firstName(),
                'last_name' => fake()->lastName(),
                'address_line_1' => fake()->streetAddress(),
                'city' => fake()->city(),
                'postal_code' => fake()->postcode(),
                'country' => 'IT',
            ],
            'subtotal' => 100,
            'shipping_amount' => 0,
            'discount_amount' => 0,
            'tax_amount' => 22,
            'total' => 122,
        ];
    }
}
