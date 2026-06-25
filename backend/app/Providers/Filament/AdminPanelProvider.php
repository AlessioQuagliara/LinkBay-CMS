<?php

namespace App\Providers\Filament;

use App\Filament\Admin\Pages\AgencyHealthPage;
use App\Filament\Admin\Pages\UsageAnalyticsPage;
use App\Filament\Admin\Resources\AgencyEntitlementResource;
use App\Filament\Admin\Resources\AgencyHealthAlertResource;
use App\Filament\Admin\Resources\AgencyResource;
use App\Filament\Admin\Resources\AiCreditPackageResource;
use App\Filament\Admin\Resources\ContactSubmissionResource;
use App\Filament\Admin\Resources\JobApplicationResource;
use App\Filament\Admin\Resources\JobPositionResource;
use App\Filament\Admin\Resources\PlanResource;
use App\Filament\Admin\Resources\PluginCatalogItemResource;
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
                ? 'admin.'.config('app.central_domain', 'linkbay-cms.com')
                : env('ADMIN_DOMAIN', 'app.linkbay-cms.test')
            )
            ->login()
            ->brandName('LinkBayCMS - Admin')
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
                ContactSubmissionResource::class,
                JobPositionResource::class,
                JobApplicationResource::class,
                PluginCatalogItemResource::class,
                AgencyEntitlementResource::class,
                AgencyHealthAlertResource::class,
            ])
            ->pages([Dashboard::class, UsageAnalyticsPage::class, AgencyHealthPage::class])
            ->widgets([GlobalStatsWidget::class])
            ->navigationGroups([
                NavigationGroup::make('Tenancy')->icon('heroicon-o-building-office-2'),
                NavigationGroup::make('Billing')->icon('heroicon-o-credit-card'),
                NavigationGroup::make('AI Credits')->icon('heroicon-o-sparkles'),
                NavigationGroup::make('Operations')->icon('heroicon-o-inbox'),
                NavigationGroup::make('Careers')->icon('heroicon-o-briefcase'),
                NavigationGroup::make('Insights')->icon('heroicon-o-chart-bar'),
                NavigationGroup::make('System')->icon('heroicon-o-cog-6-tooth'),
                NavigationGroup::make('Marketplace')->icon('heroicon-o-puzzle-piece'),
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
