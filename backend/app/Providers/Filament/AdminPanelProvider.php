<?php

namespace App\Providers\Filament;

use App\Filament\Admin\Resources\AgencyResource;
use App\Filament\Admin\Resources\AiCreditPackageResource;
use App\Filament\Admin\Resources\PlanResource;
use App\Filament\Admin\Resources\TenantResource;
use App\Filament\Admin\Widgets\GlobalStatsWidget;
use Filament\Http\Middleware\Authenticate;
use Filament\Http\Middleware\AuthenticateSession;
use Filament\Http\Middleware\DisableBladeIconComponents;
use Filament\Http\Middleware\DispatchServingFilamentEvent;
use Filament\Navigation\NavigationGroup;
use Filament\Pages\Dashboard;
use Filament\Panel;
use Filament\PanelProvider;
use Filament\Support\Colors\Color;
use Illuminate\Cookie\Middleware\AddQueuedCookiesToResponse;
use Illuminate\Cookie\Middleware\EncryptCookies;
use Illuminate\Foundation\Http\Middleware\PreventRequestForgery;
use Illuminate\Routing\Middleware\SubstituteBindings;
use Illuminate\Session\Middleware\StartSession;
use Illuminate\View\Middleware\ShareErrorsFromSession;

class AdminPanelProvider extends PanelProvider
{
    public function panel(Panel $panel): Panel
    {
        return $panel
            ->id('admin')
            ->path('linkbay-admin')
            ->domain(app()->isProduction()
                ? 'admin.' . config('app.central_domain', 'linkbay-cms.com')
                : env('ADMIN_DOMAIN', 'api.localhost')
            )
            ->login()
            ->brandName('LinkBay Admin')
            ->colors(['primary' => Color::Violet])
            ->darkMode(true)
            ->maxContentWidth('full')
            ->sidebarCollapsibleOnDesktop()
            ->authGuard('web')
            ->resources([
                AgencyResource::class,
                PlanResource::class,
                TenantResource::class,
                AiCreditPackageResource::class,
            ])
            ->pages([Dashboard::class])
            ->widgets([GlobalStatsWidget::class])
            ->navigationGroups([
                NavigationGroup::make('Tenancy')->icon('heroicon-o-building-office-2'),
                NavigationGroup::make('Billing')->icon('heroicon-o-credit-card'),
                NavigationGroup::make('AI Credits')->icon('heroicon-o-sparkles'),
                NavigationGroup::make('System')->icon('heroicon-o-cog-6-tooth'),
            ])
            ->middleware([
                EncryptCookies::class,
                AddQueuedCookiesToResponse::class,
                StartSession::class,
                AuthenticateSession::class,
                ShareErrorsFromSession::class,
                PreventRequestForgery::class,
                SubstituteBindings::class,
                DisableBladeIconComponents::class,
                DispatchServingFilamentEvent::class,
            ])
            ->authMiddleware([Authenticate::class]);
    }
}
