<?php

declare(strict_types=1);

namespace App\Filament\Agency\Pages;

use App\Filament\Agency\Concerns\ResolvesCurrentAgency;
use App\Models\Central\AuditEvent;
use App\Models\Central\User;
use Filament\Pages\Page;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Support\Collection;

class AuditLogPage extends Page
{
    use ResolvesCurrentAgency;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-shield-check';

    protected static ?string $navigationLabel = 'Audit Log';

    protected static ?string $slug = 'audit-log';

    protected string $view = 'filament.agency.pages.audit-log';

    public string $filterEvent = '';

    public string $filterUser = '';

    public string $filterDateFrom = '';

    public string $filterDateTo = '';

    // ── Access control ────────────────────────────────────────────────────────

    public static function canAccess(): bool
    {
        $member = static::currentMemberStatic();

        return $member?->isOwnerOrAdmin() ?? false;
    }

    // ── Data ─────────────────────────────────────────────────────────────────

    /**
     * Returns audit events for the current agency, newest first, max 500.
     *
     * @return Collection<int, AuditEvent>
     */
    public function events(): Collection
    {
        return $this->buildBaseQuery()
            ->with('user')
            ->orderByDesc('created_at')
            ->limit(500)
            ->get();
    }

    /**
     * Users who have at least one audit event for this agency.
     * Used to populate the actor filter dropdown.
     *
     * @return array<int|string, string>
     */
    public function actorOptions(): array
    {
        $agency = $this->agency();

        if (! $agency) {
            return [];
        }

        return User::whereIn('id',
            AuditEvent::where('agency_id', $agency->id)
                ->whereNotNull('user_id')
                ->distinct()
                ->pluck('user_id'),
        )
            ->orderBy('name')
            ->pluck('name', 'id')
            ->all();
    }

    /**
     * All distinct event types recorded for this agency.
     *
     * @return array<string, string>
     */
    public function eventTypeOptions(): array
    {
        $agency = $this->agency();

        if (! $agency) {
            return [];
        }

        $used = AuditEvent::where('agency_id', $agency->id)
            ->distinct()
            ->pluck('event')
            ->all();

        $options = [];
        foreach ($used as $event) {
            $options[$event] = AuditEvent::EVENT_LABELS[$event] ?? $event;
        }

        asort($options);

        return $options;
    }

    public function hasActiveFilters(): bool
    {
        return $this->filterEvent !== ''
            || $this->filterUser !== ''
            || $this->filterDateFrom !== ''
            || $this->filterDateTo !== '';
    }

    public function clearFilters(): void
    {
        $this->filterEvent = '';
        $this->filterUser = '';
        $this->filterDateFrom = '';
        $this->filterDateTo = '';
    }

    // ── Internals ─────────────────────────────────────────────────────────────

    private function buildBaseQuery(): Builder
    {
        $agency = $this->agency();

        $query = AuditEvent::where('agency_id', $agency?->id ?? 0);

        if ($this->filterEvent !== '') {
            $query->where('event', $this->filterEvent);
        }

        if ($this->filterUser !== '') {
            $query->where('user_id', $this->filterUser);
        }

        if ($this->filterDateFrom !== '') {
            $query->where('created_at', '>=', $this->filterDateFrom);
        }

        if ($this->filterDateTo !== '') {
            $query->where('created_at', '<=', $this->filterDateTo.' 23:59:59');
        }

        return $query;
    }
}
