<?php

namespace App\Filament\Agency\Pages;

use App\Models\Central\Agency;
use Filament\Pages\Page;

class AgencyBillingPage extends Page
{
    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-credit-card';
    protected static ?string $navigationLabel = 'Abbonamento';
    protected string $view = 'filament.agency.pages.agency-billing';

    public function agency(): ?Agency
    {
        return app()->has('current_agency') ? app('current_agency') : null;
    }

    public function planName(): string
    {
        return $this->agency()?->plan?->name ?? '—';
    }

    public function planPrice(): string
    {
        $agency = $this->agency();
        if (!$agency?->plan) return '—';
        if ($agency->billing_type === 'lifetime') return 'Lifetime (AppSumo)';
        return '€' . number_format($agency->plan->price, 2, ',', '.') . ' / ' . ($agency->plan->billing_interval === 'year' ? 'anno' : 'mese');
    }

    public function maxStores(): string
    {
        $max = $this->agency()?->plan?->limits['max_stores'] ?? null;
        return $max === null ? 'Illimitati' : (string) $max;
    }

    public function transactionFee(): string
    {
        return $this->agency()?->transactionFeePct() . '%';
    }

    public function features(): array
    {
        return $this->agency()?->plan?->limits ?? [];
    }
}
