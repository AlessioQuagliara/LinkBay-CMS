<?php

declare(strict_types=1);

namespace App\Filament\Agency\Widgets;

use App\Filament\Agency\Concerns\ResolvesCurrentAgency;
use App\Models\Central\Agency;
use App\Services\AlertItem;
use App\Services\DashboardAlertService;
use Filament\Widgets\Widget;
use Illuminate\Support\Collection;

class DashboardAlertsWidget extends Widget
{
    use ResolvesCurrentAgency;

    protected string $view = 'filament.agency.widgets.dashboard-alerts';

    /** Render before PlanUpsellWidget (sort=-1) and AgencyStatsWidget. */
    protected static ?int $sort = -2;

    protected int|string|array $columnSpan = 'full';

    public static function canView(): bool
    {
        $agency = app()->has('current_agency') ? app('current_agency') : null;

        return $agency instanceof Agency && auth()->check();
    }

    /**
     * @return Collection<int, AlertItem>
     */
    public function getAlerts(): Collection
    {
        $agency = $this->agency();

        if (! $agency) {
            return collect();
        }

        return app(DashboardAlertService::class)->resolve($agency, $this->currentMember());
    }

    public function currentMemberIsOwner(): bool
    {
        return $this->currentMember()?->isOwner() ?? false;
    }
}
