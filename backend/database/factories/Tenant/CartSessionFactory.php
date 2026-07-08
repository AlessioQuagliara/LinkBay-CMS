<?php

declare(strict_types=1);

namespace Database\Factories\Tenant;

use App\Models\Tenant\CartSession;
use Illuminate\Database\Eloquent\Factories\Factory;
use Illuminate\Support\Str;

/**
 * @extends Factory<CartSession>
 */
class CartSessionFactory extends Factory
{
    protected $model = CartSession::class;

    public function definition(): array
    {
        return [
            'session_id' => (string) Str::uuid(),
            'customer_id' => null,
            'expires_at' => now()->addDays(30),
        ];
    }
}
