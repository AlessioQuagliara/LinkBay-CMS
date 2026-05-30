<?php

declare(strict_types=1);

namespace Database\Seeders;

use App\Models\Central\Plan;
use App\Models\Central\PlatformFeeRule;
use Illuminate\Database\Seeder;

/**
 * Seed delle regole fee per piano.
 *
 * Struttura:
 * - starter    → 30% platform_share
 * - pro        → 20% platform_share
 * - business   → 10% platform_share
 * - lifetime-ltd (billing_type = lifetime) → 38% platform_share
 *
 * Eseguire DOPO PlanSeeder.
 * Idempotente: skippa se esiste già una regola attiva per quel piano.
 */
class PlatformFeeRuleSeeder extends Seeder
{
    public function run(): void
    {
        $validFrom = now()->startOfDay();

        $rules = [
            ['slug' => 'starter',      'billing_type' => null,       'fee_pct' => 0.3000, 'description' => 'Piano Starter — 30% platform share'],
            ['slug' => 'pro',          'billing_type' => null,       'fee_pct' => 0.2000, 'description' => 'Piano Pro — 20% platform share'],
            ['slug' => 'business',     'billing_type' => null,       'fee_pct' => 0.1000, 'description' => 'Piano Business — 10% platform share'],
            ['slug' => 'lifetime-ltd', 'billing_type' => 'lifetime', 'fee_pct' => 0.3800, 'description' => 'Piano AppSumo LTD — 38% platform share fisso'],
        ];

        foreach ($rules as $ruleData) {
            $plan = Plan::where('slug', $ruleData['slug'])->first();

            if (!$plan) {
                $this->command->warn("Piano '{$ruleData['slug']}' non trovato — skipping.");
                continue;
            }

            // Controlla se esiste già una regola attiva (valid_until IS NULL) per questo piano
            $existing = PlatformFeeRule::where('plan_id', $plan->id)
                ->whereNull('valid_until')
                ->first();

            if ($existing) {
                $this->command->line("  → Regola per '{$ruleData['slug']}' già presente (id={$existing->id}) — skip.");
                continue;
            }

            PlatformFeeRule::create([
                'plan_id'      => $plan->id,
                'billing_type' => $ruleData['billing_type'],
                'fee_pct'      => $ruleData['fee_pct'],
                'fee_type'     => 'platform_share',
                'valid_from'   => $validFrom,
                'valid_until'  => null,
                'description'  => $ruleData['description'],
            ]);

            $this->command->info("  ✓ Regola fee '{$ruleData['slug']}': {$ruleData['fee_pct']}");
        }

        $this->command->info('PlatformFeeRuleSeeder completato.');
    }
}
