<?php

declare(strict_types=1);

namespace Database\Seeders;

use App\Models\Central\AiCreditPackage;
use App\Models\Central\Plan;
use Illuminate\Database\Seeder;

class PlanSeeder extends Seeder
{
    public function run(): void
    {
        $plans = [
            [
                'name' => 'Starter',
                'slug' => 'starter',
                'price' => 29.00,
                'billing_interval' => 'month',
                'features' => ['products', 'orders', 'customers', 'discount_codes'],
                'limits' => [
                    'white_label' => false,
                    'custom_domain' => false,
                    'max_stores' => 5,
                    'transaction_fee_pct' => 2.5,
                    'ai_credits_monthly_bonus' => 0,
                    'layout_manager' => false,
                    'marketplace_themes' => false,
                    'marketplace_plugins' => false,
                    'priority_support' => false,
                    'hide_linkbay_branding' => false,
                ],
                'is_active' => true,
                'sort_order' => 1,
            ],
            [
                'name' => 'Pro',
                'slug' => 'pro',
                'price' => 79.00,
                'billing_interval' => 'month',
                'features' => ['products', 'orders', 'customers', 'discount_codes', 'analytics', 'api_access'],
                'limits' => [
                    'white_label' => true,
                    'custom_domain' => false,
                    'max_stores' => 20,
                    'transaction_fee_pct' => 1.5,
                    'ai_credits_monthly_bonus' => 5000,
                    'layout_manager' => false,
                    'marketplace_themes' => true,
                    'marketplace_plugins' => true,
                    'priority_support' => false,
                    'hide_linkbay_branding' => true,
                ],
                'is_active' => true,
                'sort_order' => 2,
            ],
            [
                'name' => 'Business',
                'slug' => 'business',
                'price' => 199.00,
                'billing_interval' => 'month',
                'features' => ['products', 'orders', 'customers', 'discount_codes', 'analytics', 'api_access', 'advanced_analytics', 'multi_warehouse'],
                'limits' => [
                    'white_label' => true,
                    'custom_domain' => true,
                    'max_stores' => null,
                    'transaction_fee_pct' => 0.5,
                    'ai_credits_monthly_bonus' => 20000,
                    'layout_manager' => true,
                    'marketplace_themes' => true,
                    'marketplace_plugins' => true,
                    'priority_support' => true,
                    'hide_linkbay_branding' => true,
                ],
                'is_active' => true,
                'sort_order' => 3,
            ],
            [
                'name' => 'Lifetime (AppSumo LTD)',
                'slug' => 'lifetime-ltd',
                'price' => 0.00,
                'billing_interval' => 'month',
                'features' => ['products', 'orders', 'customers', 'discount_codes', 'analytics', 'api_access'],
                'limits' => [
                    'white_label' => true,
                    'custom_domain' => false,
                    'max_stores' => 50,
                    'transaction_fee_pct' => 1.5,
                    'ai_credits_monthly_bonus' => 0,
                    'layout_manager' => false,
                    'marketplace_themes' => true,
                    'marketplace_plugins' => true,
                    'priority_support' => false,
                    'hide_linkbay_branding' => true,
                ],
                'is_active' => true,
                'sort_order' => 4,
            ],
        ];

        foreach ($plans as $data) {
            Plan::updateOrCreate(['slug' => $data['slug']], $data);
        }

        $packages = [
            ['name' => 'Starter 10K', 'credits' => 10000, 'price_cents' => 990, 'is_active' => true, 'sort_order' => 1],
            ['name' => 'Growth 50K', 'credits' => 50000, 'price_cents' => 3990, 'is_active' => true, 'sort_order' => 2],
            ['name' => 'Pro 100K', 'credits' => 100000, 'price_cents' => 6990, 'is_active' => true, 'sort_order' => 3],
            ['name' => 'Scale 500K', 'credits' => 500000, 'price_cents' => 24990, 'is_active' => true, 'sort_order' => 4],
        ];

        foreach ($packages as $data) {
            AiCreditPackage::updateOrCreate(['name' => $data['name']], $data);
        }

        $this->command->info('PlanSeeder: 4 piani + 4 pacchetti AI creati.');
    }
}
