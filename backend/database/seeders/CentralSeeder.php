<?php

declare(strict_types=1);

namespace Database\Seeders;

use App\Models\Central\Plan;
use Illuminate\Database\Seeder;

class CentralSeeder extends Seeder
{
    public function run(): void
    {
        $plans = [
            [
                'name' => 'Free',
                'slug' => 'free',
                'price' => 0,
                'billing_interval' => 'month',
                'features' => ['products', 'orders', 'customers'],
                'limits' => ['products' => 50, 'orders_per_month' => 100, 'storage_mb' => 500],
                'is_active' => true,
                'sort_order' => 1,
            ],
            [
                'name' => 'Pro',
                'slug' => 'pro',
                'price' => 29.00,
                'billing_interval' => 'month',
                'features' => ['products', 'orders', 'customers', 'discount_codes', 'analytics', 'api_access'],
                'limits' => ['products' => 500, 'orders_per_month' => 1000, 'storage_mb' => 5000],
                'is_active' => true,
                'sort_order' => 2,
            ],
            [
                'name' => 'Enterprise',
                'slug' => 'enterprise',
                'price' => 99.00,
                'billing_interval' => 'month',
                'features' => ['products', 'orders', 'customers', 'discount_codes', 'analytics', 'api_access', 'advanced_analytics', 'multi_warehouse', 'priority_support'],
                'limits' => ['products' => -1, 'orders_per_month' => -1, 'storage_mb' => 50000],
                'is_active' => true,
                'sort_order' => 3,
            ],
        ];

        foreach ($plans as $planData) {
            Plan::firstOrCreate(['slug' => $planData['slug']], $planData);
        }

        $this->command->info('Central seeder: piani creati.');
    }
}
