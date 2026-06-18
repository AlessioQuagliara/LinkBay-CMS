<?php

declare(strict_types=1);

namespace App\Services;

use App\Exceptions\InsufficientCreditsException;
use App\Models\Central\Agency;
use App\Models\Central\AiCreditLedger;
use App\Models\Central\AiCreditPackage;
use App\Models\Central\Tenant;
use Carbon\Carbon;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;
use Stripe\Checkout\Session;
use Stripe\Stripe;

class AiCreditsService
{
    public function getBalance(Agency $agency): int
    {
        return (int) AiCreditLedger::where('agency_id', $agency->id)->sum('amount');
    }

    public function hasCredits(Agency $agency, int $required = 1): bool
    {
        return $this->getBalance($agency) >= $required;
    }

    public function consume(Agency $agency, int $credits, string $description, ?string $tenantId = null): bool
    {
        return DB::connection('central')->transaction(function () use ($agency, $credits, $description, $tenantId) {
            $balance = $this->getBalance($agency);

            if ($balance < $credits) {
                throw new InsufficientCreditsException($balance, $credits);
            }

            $balanceAfter = $balance - $credits;

            AiCreditLedger::create([
                'agency_id' => $agency->id,
                'tenant_id' => $tenantId,
                'amount' => -$credits,
                'balance_after' => $balanceAfter,
                'type' => AiCreditLedger::TYPE_CONSUMPTION,
                'description' => $description,
                'created_at' => now(),
            ]);

            return true;
        });
    }

    public function purchase(Agency $agency, AiCreditPackage $package, string $paymentIntentId): void
    {
        DB::connection('central')->transaction(function () use ($agency, $package, $paymentIntentId) {
            $balance = $this->getBalance($agency);
            $balanceAfter = $balance + $package->credits;

            AiCreditLedger::create([
                'agency_id' => $agency->id,
                'tenant_id' => null,
                'amount' => $package->credits,
                'balance_after' => $balanceAfter,
                'type' => AiCreditLedger::TYPE_PURCHASE,
                'description' => "Purchase: {$package->name}",
                'stripe_payment_intent_id' => $paymentIntentId,
                'created_at' => now(),
            ]);
        });
    }

    public function addBonus(Agency $agency, int $credits, string $reason = 'Manual bonus'): void
    {
        $balance = $this->getBalance($agency);

        AiCreditLedger::create([
            'agency_id' => $agency->id,
            'amount' => $credits,
            'balance_after' => $balance + $credits,
            'type' => AiCreditLedger::TYPE_BONUS,
            'description' => $reason,
            'created_at' => now(),
        ]);
    }

    public function applyMonthlyBonus(): void
    {
        Agency::active()
            ->with('plan')
            ->each(function (Agency $agency) {
                $bonus = (int) ($agency->plan?->limits['ai_credits_monthly_bonus'] ?? 0);
                if ($bonus > 0) {
                    $this->addBonus($agency, $bonus, 'Monthly plan bonus');
                }
            });
    }

    /**
     * Consumption breakdown grouped by store, ordered by highest consumption first.
     *
     * Rows with tenant_id = null (consumption not tied to a specific store) are
     * included and labelled "Sistema" — they represent valid consumption events
     * called without a store context.
     *
     * Only this agency's stores are resolved for names; tenant_ids that no longer
     * exist in the tenants table fall back to "Store #<id>".
     *
     * @return Collection<int, object{tenant_id: string|null, store_name: string, credits_consumed: int, event_count: int, last_used_at: Carbon|null}>
     */
    public function storeBreakdown(Agency $agency, ?Carbon $since = null): Collection
    {
        $rows = AiCreditLedger::where('agency_id', $agency->id)
            ->where('type', AiCreditLedger::TYPE_CONSUMPTION)
            ->when($since, fn ($q) => $q->where('created_at', '>=', $since))
            ->selectRaw('tenant_id, ABS(SUM(amount)) as credits_consumed, COUNT(*) as event_count, MAX(created_at) as last_used_at')
            ->groupBy('tenant_id')
            ->orderByRaw('ABS(SUM(amount)) DESC')
            ->get();

        // Batch-load store names, scoped to this agency for security.
        $tenantIds = $rows->pluck('tenant_id')->filter()->unique()->values()->toArray();

        $storeNames = $tenantIds
            ? Tenant::whereIn('id', $tenantIds)
                ->where('agency_id', $agency->id)
                ->pluck('name', 'id')
                ->all()
            : [];

        return $rows->map(fn ($row) => (object) [
            'tenant_id' => $row->tenant_id,
            'store_name' => $row->tenant_id
                ? ($storeNames[$row->tenant_id] ?? "Store #{$row->tenant_id}")
                : 'Sistema',
            'credits_consumed' => (int) $row->credits_consumed,
            'event_count' => (int) $row->event_count,
            'last_used_at' => $row->last_used_at ? Carbon::parse($row->last_used_at) : null,
        ]);
    }

    public function createCheckoutSession(Agency $agency, AiCreditPackage $package): Session
    {
        Stripe::setApiKey(config('services.stripe.secret'));

        return Session::create([
            'payment_method_types' => ['card'],
            'mode' => 'payment',
            'line_items' => [[
                'price' => $package->stripe_price_id,
                'quantity' => 1,
            ]],
            'metadata' => [
                'agency_id' => $agency->id,
                'package_id' => $package->id,
                'type' => 'ai_credits',
            ],
            'success_url' => route('filament.agency.pages.ai-credits').'?purchased=1',
            'cancel_url' => route('filament.agency.pages.ai-credits'),
        ]);
    }
}
