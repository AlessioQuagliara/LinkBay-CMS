<?php

namespace App\Providers;

use Illuminate\Support\Facades\Route;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    public function register(): void {}

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
