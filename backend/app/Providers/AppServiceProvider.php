<?php

namespace App\Providers;

use App\Contracts\AgencyBillingServiceInterface;
use App\Contracts\StorePaymentServiceInterface;
use App\Services\AgencyBillingService;
use App\Services\Tenant\StorePaymentService;
use Illuminate\Queue\Events\JobFailed;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Queue;
use Illuminate\Support\Facades\Route;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    public function register(): void
    {
        $this->app->bind(AgencyBillingServiceInterface::class, AgencyBillingService::class);
        $this->app->bind(StorePaymentServiceInterface::class, StorePaymentService::class);
    }

    public function boot(): void
    {
        $this->loadMigrationsFrom([
            database_path('migrations'),
            database_path('migrations/central'),
        ]);

        Route::middleware('api')
            ->group(base_path('routes/central.php'));

        // Any queued job that exhausts its retries (webhook processing, tenant
        // provisioning, notifications) lands in failed_jobs silently otherwise.
        // 'critical' reaches the 'slack' log channel when LOG_STACK includes it
        // (see config/logging.php) — see FailedJobResource in the Admin panel
        // for manual retry/inspection.
        Queue::failing(function (JobFailed $event): void {
            Log::critical('Queue job failed', [
                'connection' => $event->connectionName,
                'job' => $event->job->resolveName(),
                'exception' => $event->exception->getMessage(),
            ]);
        });
    }
}
