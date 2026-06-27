<?php

declare(strict_types=1);

namespace App\Filament\Tenant\Widgets;

use Filament\Widgets\Widget;
use Illuminate\Support\Carbon;

class AnalyticsDateFilterWidget extends Widget
{
    protected static ?int $sort = 0;

    protected static string $view = 'filament.tenant.widgets.analytics-date-filter';

    protected int|string|array $columnSpan = 'full';

    public string $preset = '30';

    public ?string $customFrom = null;

    public ?string $customTo = null;

    public function mount(): void
    {
        $this->broadcastCurrentRange();
    }

    public function applyPreset(string $preset): void
    {
        $this->preset = $preset;
        $this->customFrom = null;
        $this->customTo = null;
        $this->broadcastCurrentRange();
    }

    public function applyCustom(): void
    {
        if ($this->customFrom && $this->customTo) {
            $this->preset = 'custom';
            $this->broadcastCurrentRange();
        }
    }

    private function broadcastCurrentRange(): void
    {
        [$from, $to] = $this->resolveRange();

        $this->dispatch('analyticsDateChanged',
            from: $from->toDateString(),
            to: $to->toDateString(),
        );
    }

    /** @return array{0: Carbon, 1: Carbon} */
    public function resolveRange(): array
    {
        if ($this->preset === 'custom' && $this->customFrom && $this->customTo) {
            return [Carbon::parse($this->customFrom), Carbon::parse($this->customTo)];
        }

        $today = now();

        return match ($this->preset) {
            'today' => [$today->copy()->startOfDay(), $today->copy()->endOfDay()],
            'yesterday' => [$today->copy()->subDay()->startOfDay(), $today->copy()->subDay()->endOfDay()],
            '7' => [$today->copy()->subDays(6)->startOfDay(), $today->copy()->endOfDay()],
            'this_month' => [$today->copy()->startOfMonth(), $today->copy()->endOfMonth()],
            'last_month' => [$today->copy()->subMonth()->startOfMonth(), $today->copy()->subMonth()->endOfMonth()],
            '90' => [$today->copy()->subDays(89)->startOfDay(), $today->copy()->endOfDay()],
            default => [$today->copy()->subDays(29)->startOfDay(), $today->copy()->endOfDay()],
        };
    }
}
