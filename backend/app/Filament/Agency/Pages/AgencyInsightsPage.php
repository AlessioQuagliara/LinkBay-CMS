<?php

declare(strict_types=1);

namespace App\Filament\Agency\Pages;

use App\Filament\Agency\Concerns\ResolvesCurrentAgency;
use App\Services\AgencyInsightsService;
use App\Services\DTO\AgencyInsightsDTO;
use Filament\Pages\Page;

class AgencyInsightsPage extends Page
{
    use ResolvesCurrentAgency;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-presentation-chart-line';

    protected static ?string $navigationLabel = 'Insights';

    protected static ?string $slug = 'insights';

    protected string $view = 'filament.agency.pages.agency-insights';

    /** @var int[] */
    public array $dayOptions = [7, 30, 90];

    public int $days = 30;

    public static function canAccess(): bool
    {
        $member = static::currentMemberStatic();

        return $member?->isOwnerOrAdmin() ?? false;
    }

    public function insightsData(): AgencyInsightsDTO
    {
        $agency = $this->agency();

        return app(AgencyInsightsService::class)->forAgency($agency, $this->days);
    }
}
