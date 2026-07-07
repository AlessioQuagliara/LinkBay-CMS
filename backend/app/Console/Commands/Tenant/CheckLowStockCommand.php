<?php

declare(strict_types=1);

namespace App\Console\Commands\Tenant;

use App\Models\Central\Tenant;
use App\Models\Tenant\User;
use App\Services\Tenant\AnalyticsService;
use Filament\Notifications\Notification;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Cache;

class CheckLowStockCommand extends Command
{
    protected $signature = 'products:check-low-stock
                            {--threshold=5 : Stock threshold under which a product is considered at risk}
                            {--dry-run : Show results without sending notifications}';

    protected $description = 'Controlla i prodotti sotto soglia in tutti i tenant e invia notifiche agli admin';

    public function handle(): int
    {
        $threshold = (int) $this->option('threshold');

        $tenants = Tenant::where('status', 'active')->get();

        if ($tenants->isEmpty()) {
            $this->warn('Nessun tenant attivo.');

            return self::SUCCESS;
        }

        foreach ($tenants as $tenant) {
            $tenant->run(function () use ($tenant, $threshold): void {
                $this->checkTenant($tenant, $threshold);
            });
        }

        return self::SUCCESS;
    }

    private function checkTenant(Tenant $tenant, int $threshold): void
    {
        $cacheKey = "low_stock_notified:{$tenant->id}";

        if (Cache::has($cacheKey)) {
            $this->line("  Tenant {$tenant->id}: notifica già inviata nelle ultime 24h — skip.");

            return;
        }

        $analytics = app(AnalyticsService::class);
        $lowStock = $analytics->getLowStockProducts($threshold);
        $outOfStock = $analytics->getOutOfStockProducts();

        $atRisk = $lowStock->count() + $outOfStock->count();

        if ($atRisk === 0) {
            $this->line("  Tenant {$tenant->id}: nessun prodotto a rischio.");

            return;
        }

        if ($this->option('dry-run')) {
            $this->warn("  [dry-run] Tenant {$tenant->id}: {$outOfStock->count()} esauriti, {$lowStock->count()} in esaurimento.");

            return;
        }

        $this->notifyTenantAdmins($tenant, $outOfStock->count(), $lowStock->count(), $threshold);

        // Prevent re-notification for 24 hours
        Cache::put($cacheKey, true, now()->addHours(24));

        $this->info("  ✓ Tenant {$tenant->id}: notifica inviata ({$atRisk} prodotti a rischio).");
    }

    private function notifyTenantAdmins(Tenant $tenant, int $outCount, int $lowCount, int $threshold): void
    {
        $admins = User::whereIn('role', ['owner', 'admin'])->get();

        $body = [];

        if ($outCount > 0) {
            $body[] = "{$outCount} prodotti esauriti";
        }

        if ($lowCount > 0) {
            $body[] = "{$lowCount} prodotti con stock ≤ {$threshold}";
        }

        foreach ($admins as $admin) {
            Notification::make()
                ->title('Attenzione: scorte in esaurimento')
                ->body(implode(' · ', $body))
                ->warning()
                ->sendToDatabase($admin);
        }
    }
}
