<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Central\UsageEvent;
use Illuminate\Support\Carbon;
use Illuminate\Support\Collection;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

/**
 * Records append-only usage events for product analytics.
 *
 * Tracking is fail-safe: any exception inside track() is caught and logged,
 * so a tracking failure never interrupts the user-facing operation.
 *
 * Agency and user context are resolved automatically from the request when
 * not provided explicitly.
 */
class UsageEventService
{
    /**
     * Record a usage event. Returns null (silently) on failure.
     *
     * @param  array<string, mixed>  $meta
     */
    public function track(
        string $eventType,
        ?string $eventGroup = null,
        ?int $agencyId = null,
        ?string $tenantId = null,
        ?int $userId = null,
        ?string $subjectType = null,
        int|string|null $subjectId = null,
        array $meta = [],
        ?Carbon $occurredAt = null,
    ): ?UsageEvent {
        try {
            return UsageEvent::create([
                'event_type' => $eventType,
                'event_group' => $eventGroup ?? $this->inferGroup($eventType),
                'agency_id' => $agencyId ?? $this->resolveAgencyId(),
                'tenant_id' => $tenantId,
                'user_id' => $userId ?? $this->resolveUserId(),
                'subject_type' => $subjectType,
                'subject_id' => $subjectId !== null ? (string) $subjectId : null,
                'meta' => empty($meta) ? null : $meta,
                'occurred_at' => $occurredAt ?? now(),
            ]);
        } catch (\Throwable $e) {
            Log::warning('UsageEventService::track failed', [
                'event_type' => $eventType,
                'error' => $e->getMessage(),
            ]);

            return null;
        }
    }

    // ── Aggregations ──────────────────────────────────────────────────────────

    /**
     * Number of agencies that generated at least one usage event in the last N days.
     */
    public function activeAgencies(int $days = 30): int
    {
        return UsageEvent::query()
            ->whereNotNull('agency_id')
            ->where('occurred_at', '>=', now()->subDays($days))
            ->distinct('agency_id')
            ->count('agency_id');
    }

    /**
     * Number of tenants/stores that generated at least one storefront.rendered event
     * in the last N days.
     */
    public function activeTenants(int $days = 30): int
    {
        return UsageEvent::query()
            ->where('event_type', UsageEvent::EVENT_STOREFRONT_RENDERED)
            ->whereNotNull('tenant_id')
            ->where('occurred_at', '>=', now()->subDays($days))
            ->distinct('tenant_id')
            ->count('tenant_id');
    }

    /**
     * Count of events of a given type in the last N days.
     * Optionally scoped to a single agency.
     */
    public function eventCount(string $eventType, int $days = 30, ?int $agencyId = null): int
    {
        return UsageEvent::query()
            ->where('event_type', $eventType)
            ->where('occurred_at', '>=', now()->subDays($days))
            ->when($agencyId !== null, fn ($q) => $q->where('agency_id', $agencyId))
            ->count();
    }

    /**
     * Top tenants ordered by total event count in the last N days.
     *
     * @return Collection<int, array{tenant_id: string, event_count: int}>
     */
    public function topTenants(int $limit = 10, int $days = 30): Collection
    {
        return UsageEvent::query()
            ->select('tenant_id', DB::raw('COUNT(*) as event_count'))
            ->whereNotNull('tenant_id')
            ->where('occurred_at', '>=', now()->subDays($days))
            ->groupBy('tenant_id')
            ->orderByDesc('event_count')
            ->limit($limit)
            ->get();
    }

    // ── Private helpers ───────────────────────────────────────────────────────

    private function resolveAgencyId(): ?int
    {
        try {
            $agency = app()->bound('current_agency') ? app('current_agency') : null;

            return $agency?->id;
        } catch (\Throwable) {
            return null;
        }
    }

    private function resolveUserId(): ?int
    {
        try {
            return auth()->id();
        } catch (\Throwable) {
            return null;
        }
    }

    private function inferGroup(string $eventType): string
    {
        return match (true) {
            str_starts_with($eventType, 'storefront.'),
            str_starts_with($eventType, 'block.'),
            str_starts_with($eventType, 'premium_block.'),
            str_starts_with($eventType, 'theme.rendered') => UsageEvent::GROUP_STOREFRONT,
            default => UsageEvent::GROUP_PANEL,
        };
    }
}
