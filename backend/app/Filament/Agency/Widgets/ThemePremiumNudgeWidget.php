<?php

declare(strict_types=1);

namespace App\Filament\Agency\Widgets;

use App\Services\FeatureAccessService;
use App\Services\PremiumPackConfig;
use Filament\Widgets\Widget;

class ThemePremiumNudgeWidget extends Widget
{
    protected string $view = 'filament.agency.widgets.theme-premium-nudge';

    protected static ?int $sort = -2;

    protected int|string|array $columnSpan = 'full';

    public static function canView(): bool
    {
        $agency = app()->has('current_agency') ? app('current_agency') : null;

        if (! $agency) {
            return false;
        }

        // Show when the agency lacks access to at least one premium theme pack.
        $service = app(FeatureAccessService::class);

        foreach (PremiumPackConfig::all() as $pack) {
            if ($pack['type'] === 'theme_pack' && ! $service->canUseFeature($agency, $pack['featureCode'])) {
                return true;
            }
        }

        return false;
    }

    /**
     * @return array<int, array{featureCode: string, label: string, description: string, type: string, includes: string[], ctaLabel: string}>
     */
    public function getUnavailableThemePacks(): array
    {
        $agency = app()->has('current_agency') ? app('current_agency') : null;

        return array_values(array_filter(
            PremiumPackConfig::unavailableFor($agency),
            fn (array $pack): bool => $pack['type'] === 'theme_pack',
        ));
    }
}
