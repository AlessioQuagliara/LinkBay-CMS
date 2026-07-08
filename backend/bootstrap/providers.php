<?php

use App\Providers\AppServiceProvider;
use App\Providers\EventServiceProvider;
use App\Providers\Filament\AdminPanelProvider;
use App\Providers\Filament\AgencyPanelProvider;
use App\Providers\Filament\TenantPanelProvider;
use App\Providers\PluginServiceProvider;
use App\Providers\TenancyServiceProvider;

return [
    AppServiceProvider::class,
    EventServiceProvider::class,
    PluginServiceProvider::class,
    TenancyServiceProvider::class,
    AdminPanelProvider::class,
    TenantPanelProvider::class,
    AgencyPanelProvider::class,
];
