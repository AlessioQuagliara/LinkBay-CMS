<?php

declare(strict_types=1);

namespace App\Console\Commands\Tenant;

use App\Models\Central\Tenant;
use App\Models\Tenant\Product;
use App\Services\Tenant\AnalyticsService;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Cache;

class ReindexTenantProductsCommand extends Command
{
    protected $signature = 'scout:import-tenant-products
                            {tenantId : ID del tenant da reindicizzare}
                            {--dry-run : Mostra quanti prodotti verrebbero reindicizzati senza agire}';

    protected $description = 'Riesegue la reindicizzazione dei prodotti per un tenant specifico (utile dopo import bulk o migrazione)';

    public function handle(): int
    {
        $tenantId = $this->argument('tenantId');
        $tenant = Tenant::find($tenantId);

        if (! $tenant) {
            $this->error("Tenant '{$tenantId}' non trovato.");

            return self::FAILURE;
        }

        $tenant->run(function () use ($tenant): void {
            $count = Product::where('is_active', true)->count();

            if ($this->option('dry-run')) {
                $this->info("[dry-run] Tenant {$tenant->id}: {$count} prodotti attivi da reindicizzare.");

                return;
            }

            $this->info("Tenant {$tenant->id}: reindicizzazione di {$count} prodotti attivi…");

            // Flush analytics cache so stale data is removed after bulk import
            app(AnalyticsService::class)->flushCache();

            // Flush product suggestion cache for this tenant
            $this->flushSuggestionCache($tenant->id);

            $this->info("  ✓ Cache analytics e suggerimenti svuotata per tenant {$tenant->id}.");
            $this->info("  ✓ {$count} prodotti pronti per ricerca.");
        });

        return self::SUCCESS;
    }

    private function flushSuggestionCache(string $tenantId): void
    {
        // Without Scout, search is DB-based so we only need to clear the
        // Redis suggestion cache keys for this tenant.
        try {
            Cache::tags(["search:{$tenantId}"])->flush();
        } catch (\Throwable) {
            // Cache driver doesn't support tags — no-op
        }
    }
}
