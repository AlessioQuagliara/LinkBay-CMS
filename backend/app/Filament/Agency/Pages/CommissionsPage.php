<?php

declare(strict_types=1);

namespace App\Filament\Agency\Pages;

use App\Filament\Agency\Concerns\ResolvesCurrentAgency;
use App\Models\Central\CommissionRecord;
use App\Models\Central\PlatformFeeRule;
use App\Models\Central\Tenant;
use App\Services\PlatformFeeService;
use Filament\Pages\Page;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;
use Symfony\Component\HttpFoundation\StreamedResponse;

class CommissionsPage extends Page
{
    use ResolvesCurrentAgency;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-banknotes';
    protected static ?string $navigationLabel = 'Commissioni';
    protected static ?string $slug = 'commissions';
    protected string $view = 'filament.agency.pages.commissions';

    public string $filterPeriod = 'month';
    public string $filterStore  = '';

    public function currentFeeRule(): ?PlatformFeeRule
    {
        $agency = $this->agency();
        if (!$agency) return null;

        try {
            return app(PlatformFeeService::class)->resolveRule($agency);
        } catch (\Throwable $e) {
            \Illuminate\Support\Facades\Log::warning('CommissionsPage: no fee rule', [
                'agency_id'    => $agency->id,
                'plan_id'      => $agency->plan_id,
                'billing_type' => $agency->billing_type,
                'error'        => $e->getMessage(),
            ]);
            return null;
        }
    }

    public function missingRulePlanName(): string
    {
        return $this->agency()?->plan?->name ?? 'nessun piano';
    }

    /**
     * Righe commissioni per la tabella — max 200, già filtrate.
     * Non usare per calcoli aggregati: usare aggregateTotals().
     */
    public function commissions(): Collection
    {
        return $this->buildBaseQuery()
            ->orderByDesc('created_at')
            ->limit(200)
            ->get();
    }

    /**
     * Totali aggregati calcolati direttamente in DB — corretti indipendentemente dal limit().
     * Esclude record refunded dai totali lordo/netto per non falsare il volume.
     */
    public function aggregateTotals(): array
    {
        $agency = $this->agency();
        if (!$agency) {
            return ['gross' => 0, 'fee' => 0, 'net' => 0, 'count' => 0];
        }

        $base = $this->buildBaseQuery();

        // Aggregati separati per settled/pending e per refunded
        $settled = (clone $base)
            ->whereIn('status', [CommissionRecord::STATUS_SETTLED, CommissionRecord::STATUS_PENDING])
            ->selectRaw('
                COUNT(*) as cnt,
                COALESCE(SUM(gross_amount_cents), 0) as gross,
                COALESCE(SUM(fee_amount_cents), 0) as fee,
                COALESCE(SUM(net_to_agency_cents), 0) as net
            ')
            ->first();

        // Fee negative dei refund (già incluse come negativi nella tabella commission_records)
        $refunds = (clone $base)
            ->where('status', CommissionRecord::STATUS_REFUNDED)
            ->selectRaw('COALESCE(SUM(fee_amount_cents), 0) as fee')
            ->first();

        return [
            'gross' => (int) ($settled->gross ?? 0),
            'fee'   => (int) ($settled->fee ?? 0) + (int) ($refunds->fee ?? 0),
            'net'   => (int) ($settled->net ?? 0),
            'count' => (int) ($settled->cnt ?? 0),
        ];
    }

    public function stores(): Collection
    {
        $agency = $this->agency();
        if (!$agency) return collect();

        return Tenant::where('agency_id', $agency->id)
            ->orderBy('name')
            ->get(['id', 'name']);
    }

    public function exportCsv(): StreamedResponse
    {
        // Per l'export leggiamo tutti i record (senza limit) ma sempre scoped sull'agency
        $rows = $this->buildBaseQuery()
            ->orderByDesc('created_at')
            ->get();

        $filename = 'commissioni-' . now()->format('Y-m-d') . '.csv';

        return response()->streamDownload(function () use ($rows) {
            $handle = fopen('php://output', 'w');

            fwrite($handle, "\xEF\xBB\xBF"); // BOM per Excel italiano

            fputcsv($handle, [
                'Data',
                'Store (tenant_id)',
                'GMV (lordo)',
                'Fee %',
                'Fee LinkBay',
                'Netto Agenzia',
                'Valuta',
                'Stato',
                'Stripe PaymentIntent',
                'Stripe Charge',
            ], ';');

            foreach ($rows as $row) {
                fputcsv($handle, [
                    $row->created_at->format('d/m/Y H:i'),
                    $row->tenant_id ?? '—',
                    number_format($row->gross_amount_cents / 100, 2, ',', '.'),
                    number_format((float) $row->fee_pct * 100, 1, ',', '.') . '%',
                    number_format($row->fee_amount_cents / 100, 2, ',', '.'),
                    number_format($row->net_to_agency_cents / 100, 2, ',', '.'),
                    strtoupper($row->currency),
                    $row->status,
                    $row->stripe_payment_intent_id ?? '',
                    $row->stripe_charge_id ?? '',
                ], ';');
            }

            fclose($handle);
        }, $filename, ['Content-Type' => 'text/csv; charset=UTF-8']);
    }

    // ── Internals ─────────────────────────────────────────────────────────────

    private function buildBaseQuery(): \Illuminate\Database\Eloquent\Builder
    {
        $agency = $this->agency();

        $query = CommissionRecord::where('agency_id', $agency?->id ?? 0)
            ->whereIn('status', [
                CommissionRecord::STATUS_SETTLED,
                CommissionRecord::STATUS_PENDING,
                CommissionRecord::STATUS_REFUNDED,
                CommissionRecord::STATUS_DISPUTED,
                CommissionRecord::STATUS_FAILED,
            ]);

        if ($this->filterPeriod === 'month') {
            $query->where('created_at', '>=', now()->startOfMonth());
        } elseif ($this->filterPeriod === 'quarter') {
            $query->where('created_at', '>=', now()->startOfQuarter());
        } elseif ($this->filterPeriod === 'year') {
            $query->where('created_at', '>=', now()->startOfYear());
        }

        if ($this->filterStore !== '') {
            $query->where('tenant_id', $this->filterStore);
        }

        return $query;
    }
}
