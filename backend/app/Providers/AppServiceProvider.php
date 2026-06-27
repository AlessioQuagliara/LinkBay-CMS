<?php

namespace App\Providers;

use App\Contracts\AgencyBillingServiceInterface;
use App\Contracts\StorePaymentServiceInterface;
use App\Services\AgencyBillingService;
use App\Services\Tenant\StorePaymentService;
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
    }
}
