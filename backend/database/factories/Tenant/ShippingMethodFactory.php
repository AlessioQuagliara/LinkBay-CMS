<?php

declare(strict_types=1);

namespace Database\Factories\Tenant;

use App\Models\Tenant\ShippingMethod;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends Factory<ShippingMethod>
 */
class ShippingMethodFactory extends Factory
{
    protected $model = ShippingMethod::class;

    public function definition(): array
    {
        return [
            'name' => fake()->randomElement(['Standard', 'Express', 'Corriere Espresso']),
            'carrier' => fake()->randomElement(['DHL', 'UPS', 'GLS', null]),
            'price' => fake()->randomFloat(2, 0, 20),
            'is_active' => true,
            'estimated_days' => fake()->numberBetween(1, 7),
        ];
    }

    public function inactive(): static
    {
        return $this->state(fn (array $attributes) => ['is_active' => false]);
    }
}
