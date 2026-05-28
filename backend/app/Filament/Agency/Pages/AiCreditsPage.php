<?php

namespace App\Filament\Agency\Pages;

use App\Models\Central\Agency;
use App\Models\Central\AiCreditLedger;
use App\Models\Central\AiCreditPackage;
use App\Services\AiCreditsService;
use Filament\Pages\Page;

class AiCreditsPage extends Page
{
    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-sparkles';
    protected static ?string $navigationLabel = 'Crediti AI';
    protected string $view = 'filament.agency.pages.ai-credits';

    public function agency(): ?Agency
    {
        return app()->has('current_agency') ? app('current_agency') : null;
    }

    public function balance(): int
    {
        $agency = $this->agency();
        return $agency ? app(AiCreditsService::class)->getBalance($agency) : 0;
    }

    public function packages()
    {
        return AiCreditPackage::active()->get();
    }

    public function ledger()
    {
        $agency = $this->agency();
        if (!$agency) return collect();

        return AiCreditLedger::where('agency_id', $agency->id)
            ->orderByDesc('created_at')
            ->limit(20)
            ->get();
    }

    public function checkoutUrl(int $packageId): ?string
    {
        $agency = $this->agency();
        $package = AiCreditPackage::find($packageId);
        if (!$agency || !$package) return null;

        try {
            $session = app(AiCreditsService::class)->createCheckoutSession($agency, $package);
            return $session->url;
        } catch (\Throwable) {
            return null;
        }
    }
}
