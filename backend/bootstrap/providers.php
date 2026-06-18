<?php

use App\Providers\AppServiceProvider;
use App\Providers\Filament\AdminPanelProvider;
use App\Providers\Filament\AgencyPanelProvider;
use App\Providers\Filament\TenantPanelProvider;
use App\Providers\PluginServiceProvider;
use App\Providers\TenancyServiceProvider;

return [
    AppServiceProvider::class,
    PluginServiceProvider::class,
    TenancyServiceProvider::class,
    AdminPanelProvider::class,
    TenantPanelProvider::class,
    AgencyPanelProvider::class,
];
