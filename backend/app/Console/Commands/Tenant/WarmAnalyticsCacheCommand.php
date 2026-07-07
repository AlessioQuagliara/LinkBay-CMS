<?php

declare(strict_types=1);

namespace App\Console\Commands\Tenant;

use App\Services\Tenant\AnalyticsService;
use Illuminate\Console\Command;
use Illuminate\Support\Collection;
use Stancl\Tenancy\Database\Models\Tenant;

class WarmAnalyticsCacheCommand extends Command
{
    protected $signature = 'analytics:warm-cache
                            {--tenant= : Warm a specific tenant ID only}
                            {--dry-run : Show what would be warmed without executing}';

    protected $description = 'Pre-calcola e mette in cache le metriche analytics comuni per tutti i tenant attivi';

    public function handle(): int
    {
        $tenants = $this->resolveTenants();

        if ($tenants->isEmpty()) {
            $this->warn('Nessun tenant attivo trovato.');

            return self::SUCCESS;
        }

        $this->info("Warming analytics cache per {$tenants->count()} tenant…");

        foreach ($tenants as $tenant) {
            if ($this->option('dry-run')) {
                $this->line("  [dry-run] Tenant: {$tenant->id}");

                continue;
            }

            $tenant->run(function () use ($tenant): void {
                $this->warmForTenant();
                $this->line("  ✓ Tenant {$tenant->id} completato");
            });
        }

        $this->info('Cache warming completato.');

        return self::SUCCESS;
    }

    private function warmForTenant(): void
    {
        $analytics = app(AnalyticsService::class);

        $periods = [
            [now()->subDays(6)->startOfDay(), now()->endOfDay()],
            [now()->subDays(29)->startOfDay(), now()->endOfDay()],
            [now()->subDays(89)->startOfDay(), now()->endOfDay()],
        ];

        foreach ($periods as [$from, $to]) {
            $analytics->getRevenueTotal($from, $to);
            $analytics->getOrdersCount($from, $to);
            $analytics->getAverageOrderValue($from, $to);
            $analytics->getNewCustomersCount($from, $to);
            $analytics->getRevenuePeriod($from, $to, 'day');
            $analytics->getTopProducts($from, $to);
        }
    }

    private function resolveTenants(): Collection
    {
        $specificId = $this->option('tenant');

        // Use Stancl's tenant model — resolved via tenancy() or directly
        $tenantModel = app(Tenant::class);

        if ($specificId) {
            return $tenantModel->newQuery()->where('id', $specificId)->get();
        }

        return $tenantModel->newQuery()->get();
    }
}
