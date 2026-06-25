<?php

declare(strict_types=1);

namespace App\Filament\Admin\Pages;

use App\Models\Central\UsageEvent;
use App\Services\UsageEventService;
use Filament\Pages\Page;
use Illuminate\Support\Collection;

class UsageAnalyticsPage extends Page
{
    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-chart-bar-square';

    protected static ?string $navigationLabel = 'Usage Analytics';

    protected static string|\UnitEnum|null $navigationGroup = 'System';

    protected static ?int $navigationSort = 10;

    protected static ?string $slug = 'usage-analytics';

    protected string $view = 'filament.admin.pages.usage-analytics';

    // ── Stats ─────────────────────────────────────────────────────────────────

    /**
     * @return array<string, int>
     */
    public function stats(): array
    {
        $svc = app(UsageEventService::class);

        return [
            'active_agencies_30d' => $svc->activeAgencies(30),
            'active_tenants_30d' => $svc->activeTenants(30),
            'storefronts_rendered_30d' => $svc->eventCount(UsageEvent::EVENT_STOREFRONT_RENDERED, 30),
            'premium_themes_30d' => $svc->eventCount(UsageEvent::EVENT_THEME_RENDERED, 30),
            'premium_blocks_30d' => $svc->eventCount(UsageEvent::EVENT_PREMIUM_BLOCK_RENDERED, 30),
            'forks_created_30d' => $svc->eventCount(UsageEvent::EVENT_THEME_FORK_CREATED, 30),
        ];
    }

    /**
     * @return Collection<int, object{tenant_id: string, event_count: int}>
     */
    public function topTenants(): Collection
    {
        return app(UsageEventService::class)->topTenants(10, 30);
    }

    /**
     * @return Collection<int, UsageEvent>
     */
    public function recentEvents(): Collection
    {
        return UsageEvent::with('agency')
            ->orderByDesc('occurred_at')
            ->limit(30)
            ->get();
    }
}
