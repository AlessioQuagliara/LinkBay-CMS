<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Central\Agency;
use App\Models\Central\PlatformFeeRule;
use Carbon\Carbon;
use RuntimeException;

class PlatformFeeService
{
    /**
     * Risolve la regola fee attiva per l'agency in un dato momento.
     *
     * Priorità di matching (dal più specifico al più generico):
     *   1. plan_id + billing_type corrispondenti
     *   2. plan_id corrispondente, billing_type NULL (si applica a tutti i tipi)
     *   3. plan_id NULL + billing_type corrispondente (regola globale per tipo)
     *   4. plan_id NULL + billing_type NULL (fallback globale)
     *
     * Questa priorità è espressa con ORDER BY plan_id IS NULL ASC, billing_type IS NULL ASC.
     */
    public function resolveRule(Agency $agency, ?Carbon $at = null): PlatformFeeRule
    {
        $at ??= now();

        $rule = PlatformFeeRule::query()
            ->where(function ($q) use ($agency) {
                $q->where('plan_id', $agency->plan_id)
                  ->orWhereNull('plan_id');
            })
            ->where(function ($q) use ($agency) {
                $q->where('billing_type', $agency->billing_type)
                  ->orWhereNull('billing_type');
            })
            ->where('valid_from', '<=', $at)
            ->where(function ($q) use ($at) {
                $q->whereNull('valid_until')
                  ->orWhere('valid_until', '>', $at);
            })
            // Più specifico prima: plan_id NOT NULL > NULL; billing_type NOT NULL > NULL
            ->orderByRaw('(plan_id IS NULL) ASC')
            ->orderByRaw('(billing_type IS NULL) ASC')
            ->orderByDesc('valid_from')
            ->first();

        if (!$rule) {
            throw new RuntimeException(
                "No active platform_fee_rule for agency #{$agency->id} "
                . "(plan_id={$agency->plan_id}, billing_type={$agency->billing_type}) at {$at}"
            );
        }

        return $rule;
    }

    /**
     * Calcola la fee in centesimi dato un importo lordo e una regola.
     */
    public function calculateFee(int $grossCents, PlatformFeeRule $rule): int
    {
        return (int) round($grossCents * (float) $rule->fee_pct);
    }

    /**
     * Calcola il netto all'agency (lordo - fee).
     */
    public function calculateNet(int $grossCents, int $feeCents): int
    {
        return $grossCents - $feeCents;
    }
}
