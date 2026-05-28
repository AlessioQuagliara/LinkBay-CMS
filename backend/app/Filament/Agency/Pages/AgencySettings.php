<?php

namespace App\Filament\Agency\Pages;

use App\Models\Central\Agency;
use App\Services\StripeConnectService;
use Filament\Notifications\Notification;
use Filament\Pages\Page;

class AgencySettings extends Page
{
    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-cog-6-tooth';
    protected static ?string $navigationLabel = 'Impostazioni';
    protected string $view = 'filament.agency.pages.agency-settings';

    public array $brandData = [];
    public array $domainData = [];

    public function mount(): void
    {
        $agency = $this->agency();
        if ($agency) {
            $this->brandData = [
                'brand_name' => $agency->brand_name,
                'logo_url' => $agency->logo_url,
                'favicon_url' => $agency->favicon_url,
                'primary_color' => $agency->primary_color ?? '#f59e0b',
                'support_email' => $agency->support_email,
                'support_url' => $agency->support_url,
            ];
            $this->domainData = [
                'custom_domain' => $agency->custom_domain,
                'hide_linkbay_branding' => $agency->hide_linkbay_branding,
            ];
        }
    }

    public function canAccessWhiteLabel(): bool
    {
        return (bool) $this->agency()?->canUseFeature('white_label');
    }

    public function canAccessCustomDomain(): bool
    {
        return (bool) $this->agency()?->canUseFeature('custom_domain');
    }

    public function stripeIsOnboarded(): bool
    {
        return (bool) $this->agency()?->stripe_connect_onboarded;
    }

    public function getStripeConnectUrl(): ?string
    {
        $agency = $this->agency();
        if (!$agency || $agency->stripe_connect_onboarded) {
            return null;
        }
        try {
            return app(StripeConnectService::class)->createOnboardingLink($agency);
        } catch (\Throwable) {
            return null;
        }
    }

    public function currentTransactionFee(): string
    {
        return $this->agency()?->transactionFeePct() . '%';
    }

    public function saveBrand(): void
    {
        $agency = $this->agency();
        if (!$agency?->canUseFeature('white_label')) {
            Notification::make()->title('Upgrade required per White-Label')->warning()->send();
            return;
        }
        $agency->update($this->brandData);
        Notification::make()->title('Brand aggiornato')->success()->send();
    }

    public function saveDomain(): void
    {
        $agency = $this->agency();
        if (!$agency?->canUseFeature('custom_domain')) {
            Notification::make()->title('Upgrade a Business per dominio custom')->warning()->send();
            return;
        }
        $agency->update(['custom_domain' => $this->domainData['custom_domain'] ?? null]);
        Notification::make()->title('Dominio salvato')->success()->send();
    }

    private function agency(): ?Agency
    {
        return app()->has('current_agency') ? app('current_agency') : null;
    }
}
