<?php

namespace App\Providers\Filament;

use App\Filament\Tenant\Pages\StoreSettings;
use App\Filament\Tenant\Resources\CollectionResource;
use App\Filament\Tenant\Resources\CustomerResource;
use App\Filament\Tenant\Resources\DiscountCodeResource;
use App\Filament\Tenant\Resources\OrderResource;
use App\Filament\Tenant\Resources\ProductResource;
use App\Filament\Tenant\Resources\ShippingMethodResource;
use App\Filament\Tenant\Widgets\LatestOrdersWidget;
use App\Filament\Tenant\Widgets\RevenueChartWidget;
use App\Filament\Tenant\Widgets\TenantStatsOverviewWidget;
use App\Models\Tenant\User;
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
use Stancl\Tenancy\Middleware\InitializeTenancyByDomain;
use Stancl\Tenancy\Middleware\PreventAccessFromCentralDomains;

class TenantPanelProvider extends PanelProvider
{
    public function panel(Panel $panel): Panel
    {
        [$brandName, $primaryColor, $logoUrl, $hideFooter] = $this->resolveBranding();

        $built = $panel
            ->id('tenant')
            ->path('admin')
            ->login()
            ->brandName($brandName)
            ->colors(['primary' => $primaryColor])
            ->darkMode(true)
            ->maxContentWidth('full')
            ->sidebarCollapsibleOnDesktop()
            ->authGuard('tenant_web')
            ->resources([
                ProductResource::class,
                CollectionResource::class,
                OrderResource::class,
                CustomerResource::class,
                DiscountCodeResource::class,
                ShippingMethodResource::class,
            ])
            ->pages([Dashboard::class, StoreSettings::class])
            ->widgets([
                TenantStatsOverviewWidget::class,
                RevenueChartWidget::class,
                LatestOrdersWidget::class,
            ])
            ->navigationGroups([
                NavigationGroup::make('Catalogo')->icon('heroicon-o-archive-box'),
                NavigationGroup::make('Vendite')->icon('heroicon-o-shopping-cart'),
                NavigationGroup::make('Marketing')->icon('heroicon-o-megaphone'),
                NavigationGroup::make('Impostazioni')->icon('heroicon-o-cog-6-tooth'),
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
                InitializeTenancyByDomain::class,
                PreventAccessFromCentralDomains::class,
            ])
            ->authMiddleware([Authenticate::class])
            ->renderHook(
                'panels::footer',
                fn () => $hideFooter ? '' : '<p class="text-center text-xs text-gray-400 py-2">Powered by <a href="https://linkbay-cms.com" class="underline">LinkBay</a></p>',
            );

        if ($logoUrl) {
            $built->brandLogo($logoUrl);
        }

        return $built;
    }

    private function resolveBranding(): array
    {
        try {
            $tenantInstance = tenancy()->initialized() ? tenant() : null;
        } catch (\Throwable) {
            $tenantInstance = null;
        }

        // Try to load agency from request host
        $agency = null;
        try {
            if ($tenantInstance) {
                $agency = $tenantInstance->agency;
            }
        } catch (\Throwable) {}

        if ($agency && $agency->canUseFeature('white_label')) {
            return [
                $agency->brand_name,
                Color::hex($agency->resolvedPrimaryColor()),
                $agency->logo_url,
                (bool) ($agency->plan?->limits['hide_linkbay_branding'] ?? false),
            ];
        }

        $storeName = 'My Store';
        try {
            $storeName = \App\Models\Tenant\Setting::get('store_name', 'My Store') ?? 'My Store';
        } catch (\Throwable) {}

        return [$storeName, Color::Amber, null, false];
    }
}
