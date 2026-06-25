<?php

declare(strict_types=1);

namespace App\Filament\Admin\Pages;

use App\Enums\ActivityLevel;
use App\Enums\PremiumAdoptionLevel;
use App\Models\Central\AgencyEntitlement;
use App\Services\AgencyHealthService;
use App\Services\DTO\AgencyHealthDTO;
use App\Services\UsageEventService;
use Filament\Pages\Page;
use Illuminate\Support\Collection;

class AgencyHealthPage extends Page
{
    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-heart';

    protected static ?string $navigationLabel = 'Agency Health';

    protected static string|\UnitEnum|null $navigationGroup = 'Insights';

    protected static ?int $navigationSort = 10;

    protected static ?string $slug = 'agency-health';

    protected string $view = 'filament.admin.pages.agency-health';

    // ── Filter state (Livewire-reactive) ──────────────────────────────────────

    public int $days = 30;

    public ?string $filterActivityLevel = null;

    public ?string $filterPremiumAdoption = null;

    // ── Data methods ──────────────────────────────────────────────────────────

    /**
     * Summary KPIs shown in the header — simple counts, fast queries.
     *
     * @return array{active_agencies: int, active_tenants: int, premium_pack_agencies: int}
     */
    public function summaryStats(): array
    {
        $svc = app(UsageEventService::class);

        return [
            'active_agencies' => $svc->activeAgencies($this->days),
            'active_tenants' => $svc->activeTenants($this->days),
            'premium_pack_agencies' => AgencyEntitlement::query()
                ->where('status', AgencyEntitlement::STATUS_ACTIVE)
                ->distinct('agency_id')
                ->count('agency_id'),
        ];
    }

    /**
     * Full health dataset, filtered by the current Livewire state.
     *
     * @return Collection<int, AgencyHealthDTO>
     */
    public function healthData(): Collection
    {
        $data = app(AgencyHealthService::class)->summaryForAllAgencies($this->days);

        if ($this->filterActivityLevel !== null) {
            $data = $data->filter(
                fn (AgencyHealthDTO $dto) => $dto->activityLevel->value === $this->filterActivityLevel
            );
        }

        if ($this->filterPremiumAdoption !== null) {
            $data = $data->filter(
                fn (AgencyHealthDTO $dto) => $dto->premiumAdoptionLevel->value === $this->filterPremiumAdoption
            );
        }

        return $data->values();
    }

    /**
     * Available filter options for the activity level dropdown.
     *
     * @return array<string, string>
     */
    public function activityLevelOptions(): array
    {
        return collect(ActivityLevel::cases())
            ->mapWithKeys(fn (ActivityLevel $l) => [$l->value => $l->label()])
            ->all();
    }

    /**
     * Available filter options for the premium adoption dropdown.
     *
     * @return array<string, string>
     */
    public function premiumAdoptionOptions(): array
    {
        return collect(PremiumAdoptionLevel::cases())
            ->mapWithKeys(fn (PremiumAdoptionLevel $l) => [$l->value => $l->label()])
            ->all();
    }
}
