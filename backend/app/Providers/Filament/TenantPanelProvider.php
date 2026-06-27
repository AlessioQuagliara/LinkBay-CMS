<?php

namespace App\Providers\Filament;

use App\Filament\Tenant\Pages\BrandSettingsPage;
use App\Filament\Tenant\Pages\LanguageSettingsPage;
use App\Filament\Tenant\Pages\MediaLibraryPage;
use App\Filament\Tenant\Pages\StoreSettings;
use App\Filament\Tenant\Pages\TeamPage;
use App\Filament\Tenant\Resources\CollectionResource;
use App\Filament\Tenant\Resources\CustomerResource;
use App\Filament\Tenant\Resources\DiscountCodeResource;
use App\Filament\Tenant\Resources\OrderResource;
use App\Filament\Tenant\Resources\ProductResource;
use App\Filament\Tenant\Resources\ShippingMethodResource;
use App\Filament\Tenant\Resources\StorePageResource;
use App\Filament\Tenant\Widgets\LatestOrdersWidget;
use App\Filament\Tenant\Widgets\RevenueChartWidget;
use App\Filament\Tenant\Widgets\TenantStatsOverviewWidget;
use App\Models\Tenant\Setting;
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
        [$brandName, $primaryColor, $logoUrl, $hideFooter, $faviconUrl] = $this->resolveBranding();

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
            ->passwordReset()
            ->authPasswordBroker('tenant_users')
            ->resources([
                ProductResource::class,
                CollectionResource::class,
                OrderResource::class,
                CustomerResource::class,
                DiscountCodeResource::class,
                ShippingMethodResource::class,
                StorePageResource::class,
            ])
            ->pages([
                Dashboard::class,
                StoreSettings::class,
                TeamPage::class,
                BrandSettingsPage::class,
                LanguageSettingsPage::class,
                MediaLibraryPage::class,
            ])
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
                // Tenancy MUST initialise before session so the tenant_web guard
                // reads users from the correct tenant DB, not the central DB.
                InitializeTenancyByDomain::class,
                PreventAccessFromCentralDomains::class,
                StartSession::class,
                AuthenticateSession::class,
                ShareErrorsFromSession::class,
                PreventRequestForgery::class,
                SubstituteBindings::class,
                DisableBladeIconComponents::class,
                DispatchServingFilamentEvent::class,
            ])
            ->authMiddleware([Authenticate::class])
            ->renderHook(
                'panels::footer',
                fn () => $hideFooter ? '' : view('filament.partials.powered-by')->render(),
            );

        if ($logoUrl) {
            $built->brandLogo($logoUrl);
        }

        if ($faviconUrl) {
            $built->favicon($faviconUrl);
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
        } catch (\Throwable) {
        }

        if ($agency && $agency->canUseFeature('white_label')) {
            return [
                $agency->brand_name,
                Color::hex($agency->resolvedPrimaryColor()),
                $agency->logo_url,
                (bool) ($agency->plan?->limits['hide_linkbay_branding'] ?? false),
                $agency->favicon_url,
            ];
        }

        $storeName = 'My Store';
        try {
            $storeName = Setting::get('store_name', 'My Store') ?? 'My Store';
        } catch (\Throwable) {
        }

        return [$storeName, Color::Amber, null, false, null];
    }
}
