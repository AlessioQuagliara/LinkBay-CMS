<?php

namespace App\Filament\Agency\Widgets;

use App\Models\Central\Plan;
use Filament\Widgets\Widget;
use Illuminate\Database\Eloquent\Collection;

class PlanUpsellWidget extends Widget
{
    protected string $view = 'filament.agency.widgets.plan-upsell';

    protected static ?int $sort = -1;

    protected int|string|array $columnSpan = 'full';

    public static function canView(): bool
    {
        $agency = app()->has('current_agency') ? app('current_agency') : null;

        return $agency && $agency->plan_id === null;
    }

    public function getPlans(): Collection
    {
        return Plan::where('is_active', true)->orderBy('sort_order')->orderBy('price')->get();
    }
}
