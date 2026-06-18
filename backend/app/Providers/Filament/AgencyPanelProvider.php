<?php

namespace App\Providers\Filament;

use App\Filament\Agency\Pages\AgencyBillingPage;
use App\Filament\Agency\Pages\AgencySettings;
use App\Filament\Agency\Pages\AiCreditsPage;
use App\Filament\Agency\Pages\AuditLogPage;
use App\Filament\Agency\Pages\CommissionsPage;
use App\Filament\Agency\Pages\PayoutsPage;
use App\Filament\Agency\Pages\TermsAcceptancePage;
use App\Filament\Agency\Resources\AgencyClientResource;
use App\Filament\Agency\Resources\AgencyMemberResource;
use App\Filament\Agency\Resources\LayoutTemplateResource;
use App\Filament\Agency\Resources\StoreResource;
use App\Filament\Agency\Resources\ThemePresetResource;
use App\Filament\Agency\Widgets\AgencyStatsWidget;
use App\Filament\Agency\Widgets\DashboardAlertsWidget;
use App\Filament\Agency\Widgets\PlanUpsellWidget;
use App\Http\Middleware\EnsureValidAgencyDomain;
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
use Illuminate\Support\Facades\Log;
use Illuminate\View\Middleware\ShareErrorsFromSession;

class AgencyPanelProvider extends PanelProvider
{
    public function register(): void
    {
        parent::register();

        // Lazy singleton for non-HTTP contexts (console, queue).
        // In HTTP requests EnsureValidAgencyDomain is authoritative and overrides
        // this binding via app()->instance() before any panel code runs.
        $this->app->singleton('current_agency', function () {
            if (app()->runningInConsole()) {
                return null;
            }

            try {
                return Agency::fromDomain(request()->getHost());
            } catch (\Throwable $e) {
                Log::warning('AgencyPanelProvider: failed to resolve current_agency', [
                    'error' => $e->getMessage(),
                    'host' => request()->getHost(),
                ]);

                return null;
            }
        });
    }

    public function panel(Panel $panel): Panel
    {
        $built = $panel
            ->id('agency')
            ->path('dashboard')
            ->login()
            // Closures keep branding lazy: resolved at render time after
            // EnsureValidAgencyDomain has bound the correct agency instance.
            ->brandName(fn () => app('current_agency')?->brand_name ?? 'Agency Dashboard')
            ->colors(fn () => ['primary' => Color::hex(app('current_agency')?->resolvedPrimaryColor() ?? '#ff5758')])
            ->darkMode(true)
            ->maxContentWidth('full')
            ->sidebarCollapsibleOnDesktop()
            ->viteTheme('resources/css/filament-agency.css')
            ->authGuard('web')
            ->resources([StoreResource::class, AgencyClientResource::class, AgencyMemberResource::class, LayoutTemplateResource::class, ThemePresetResource::class])
            ->pages([
                Dashboard::class,
                AgencySettings::class,
                AgencyBillingPage::class,
                AiCreditsPage::class,
                CommissionsPage::class,
                PayoutsPage::class,
                AuditLogPage::class,
                TermsAcceptancePage::class,
            ])
            ->widgets([DashboardAlertsWidget::class, PlanUpsellWidget::class, AgencyStatsWidget::class])
            ->middleware([
                EncryptCookies::class,
                AddQueuedCookiesToResponse::class,
                // Domain validation runs before session so an invalid domain
                // never touches the session store and never triggers auth.
                EnsureValidAgencyDomain::class,
                StartSession::class,
                AuthenticateSession::class,
                ShareErrorsFromSession::class,
                PreventRequestForgery::class,
                SubstituteBindings::class,
                DisableBladeIconComponents::class,
                DispatchServingFilamentEvent::class,
            ])
            ->authMiddleware([Authenticate::class, RequireTermsAcceptance::class]);

        // Logo and favicon are also closures so they resolve after domain validation.
        $built->brandLogo(fn () => app('current_agency')?->logo_url);
        $built->favicon(fn () => app('current_agency')?->favicon_url);

        return $built;
    }
}
