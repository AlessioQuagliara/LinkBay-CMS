<?php

namespace App\Providers\Filament;

use App\Filament\Agency\Pages\AgencyBillingPage;
use App\Filament\Agency\Pages\AgencySettings;
use App\Filament\Agency\Pages\AiCreditsPage;
use App\Filament\Agency\Resources\StoreResource;
use App\Models\Central\Agency;
use Filament\Http\Middleware\Authenticate;
use Filament\Http\Middleware\AuthenticateSession;
use Filament\Http\Middleware\DisableBladeIconComponents;
use Filament\Http\Middleware\DispatchServingFilamentEvent;
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

class AgencyPanelProvider extends PanelProvider
{
    public function register(): void
    {
        parent::register();

        try {
            $host = request()->getHost();
            $agency = Agency::where('custom_domain', $host)
                ->orWhere('slug', explode('.', $host)[0])
                ->first();

            app()->instance('current_agency', $agency);
        } catch (\Throwable) {
            app()->instance('current_agency', null);
        }
    }

    public function panel(Panel $panel): Panel
    {
        $agency = app()->has('current_agency') ? app('current_agency') : null;

        if (!$agency) {
            // Fall back to defaults — the actual 404 is handled in boot()
            return $panel
                ->id('agency')
                ->path('dashboard')
                ->login()
                ->brandName('Agency Dashboard')
                ->colors(['primary' => Color::Amber])
                ->darkMode(true)
                ->maxContentWidth('full')
                ->sidebarCollapsibleOnDesktop()
                ->authGuard('web')
                ->resources([StoreResource::class])
                ->pages([Dashboard::class, AgencySettings::class, AgencyBillingPage::class, AiCreditsPage::class])
                ->middleware($this->defaultMiddleware())
                ->authMiddleware([Authenticate::class]);
        }

        $built = $panel
            ->id('agency')
            ->path('dashboard')
            ->login()
            ->brandName($agency->brand_name)
            ->colors(['primary' => Color::hex($agency->resolvedPrimaryColor())])
            ->darkMode(true)
            ->maxContentWidth('full')
            ->sidebarCollapsibleOnDesktop()
            ->authGuard('web')
            ->resources([StoreResource::class])
            ->pages([Dashboard::class, AgencySettings::class, AgencyBillingPage::class, AiCreditsPage::class])
            ->middleware($this->defaultMiddleware())
            ->authMiddleware([Authenticate::class]);

        if ($agency->logo_url) {
            $built->brandLogo($agency->logo_url);
        }
        if ($agency->favicon_url) {
            $built->favicon($agency->favicon_url);
        }

        return $built;
    }

    private function defaultMiddleware(): array
    {
        return [
            EncryptCookies::class,
            AddQueuedCookiesToResponse::class,
            StartSession::class,
            AuthenticateSession::class,
            ShareErrorsFromSession::class,
            PreventRequestForgery::class,
            SubstituteBindings::class,
            DisableBladeIconComponents::class,
            DispatchServingFilamentEvent::class,
        ];
    }
}
