<?php

declare(strict_types=1);

namespace Database\Factories\Tenant;

use App\Models\Tenant\DiscountCode;
use Illuminate\Database\Eloquent\Factories\Factory;
use Illuminate\Support\Str;

/**
 * @extends Factory<DiscountCode>
 */
class DiscountCodeFactory extends Factory
{
    protected $model = DiscountCode::class;

    public function definition(): array
    {
        return [
            'code' => Str::upper(Str::random(8)),
            'type' => DiscountCode::TYPE_PERCENTAGE,
            'value' => 10,
            'usage_limit' => null,
            'used_count' => 0,
            'minimum_amount' => null,
            'expires_at' => null,
            'is_active' => true,
        ];
    }

    public function fixed(float $value): static
    {
        return $this->state(fn (array $attributes) => [
            'type' => DiscountCode::TYPE_FIXED,
            'value' => $value,
        ]);
    }

    public function freeShipping(): static
    {
        return $this->state(fn (array $attributes) => [
            'type' => DiscountCode::TYPE_FREE_SHIPPING,
            'value' => 0,
        ]);
    }

    public function expired(): static
    {
        return $this->state(fn (array $attributes) => [
            'expires_at' => now()->subDay(),
        ]);
    }

    public function inactive(): static
    {
        return $this->state(fn (array $attributes) => ['is_active' => false]);
    }

    public function exhausted(): static
    {
        return $this->state(fn (array $attributes) => [
            'usage_limit' => 1,
            'used_count' => 1,
        ]);
    }
}
