<?php

namespace App\Providers\Filament;

use App\Filament\Agency\Pages\AgencyBillingPage;
use App\Filament\Agency\Pages\AgencySettings;
use App\Filament\Agency\Pages\AiCreditsPage;
use App\Filament\Agency\Pages\CommissionsPage;
use App\Filament\Agency\Pages\TermsAcceptancePage;
use App\Filament\Agency\Resources\AgencyClientResource;
use App\Filament\Agency\Resources\StoreResource;
use App\Filament\Agency\Widgets\AgencyStatsWidget;
use App\Filament\Agency\Widgets\PlanUpsellWidget;
use App\Http\Middleware\RequireTermsAcceptance;
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

        // Lazy singleton: il DB query viene eseguito solo al primo accesso a app('current_agency'),
        // non durante register() dove il resolver Eloquent potrebbe non essere ancora pronto.
        $this->app->singleton('current_agency', function () {
            try {
                if (app()->runningInConsole()) {
                    return null;
                }
                $host = request()->getHost();
                return Agency::where('custom_domain', $host)
                    ->orWhere('slug', explode('.', $host)[0])
                    ->first();
            } catch (\Throwable $e) {
                \Illuminate\Support\Facades\Log::warning('AgencyPanelProvider: failed to resolve current_agency', [
                    'error' => $e->getMessage(),
                    'host'  => request()->getHost(),
                ]);
                return null;
            }
        });
    }

    public function panel(Panel $panel): Panel
    {
        $agency = app('current_agency');

        $pages = [
            Dashboard::class,
            AgencySettings::class,
            AgencyBillingPage::class,
            AiCreditsPage::class,
            CommissionsPage::class,
            TermsAcceptancePage::class,
        ];

        $widgets = [
            PlanUpsellWidget::class,
            AgencyStatsWidget::class,
        ];

        if (!$agency) {
            return $panel
                ->id('agency')
                ->path('dashboard')
                ->login()
                ->brandName('Agency Dashboard')
                ->colors(['primary' => Color::hex('#ff5758')])
                ->darkMode(true)
                ->maxContentWidth('full')
                ->sidebarCollapsibleOnDesktop()
                ->viteTheme('resources/css/filament-agency.css')
                ->authGuard('web')
                ->resources([StoreResource::class, AgencyClientResource::class])
                ->pages($pages)
                ->widgets($widgets)
                ->middleware($this->defaultMiddleware())
                ->authMiddleware([Authenticate::class, RequireTermsAcceptance::class]);
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
            ->viteTheme('resources/css/filament-agency.css')
            ->authGuard('web')
            ->resources([StoreResource::class, AgencyClientResource::class])
            ->pages($pages)
            ->widgets($widgets)
            ->middleware($this->defaultMiddleware())
            ->authMiddleware([Authenticate::class, RequireTermsAcceptance::class]);

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
