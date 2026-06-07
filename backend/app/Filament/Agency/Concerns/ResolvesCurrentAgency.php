<?php

declare(strict_types=1);

namespace App\Filament\Agency\Concerns;

use App\Models\Central\Agency;
use App\Models\Central\AgencyMember;

trait ResolvesCurrentAgency
{
    protected function agency(): ?Agency
    {
        // EnsureValidAgencyDomain runs before any Filament page/component and
        // always binds the agency via app()->instance(), so a simple container
        // lookup is sufficient.  We load the plan relation on first access.
        $agency = app()->bound('current_agency') ? app('current_agency') : null;

        if (! $agency instanceof Agency) {
            return null;
        }

        if (! $agency->relationLoaded('plan')) {
            $agency->load('plan');
        }

        return $agency;
    }

    /**
     * Returns the authenticated user's active AgencyMember for the current agency.
     * Null when unauthenticated, no agency resolved, or no active membership found.
     */
    protected function currentMember(): ?AgencyMember
    {
        $agency = $this->agency();
        $user = auth()->user();

        if (! $agency || ! $user) {
            return null;
        }

        return AgencyMember::where('agency_id', $agency->id)
            ->where('user_id', $user->id)
            ->where('status', AgencyMember::STATUS_ACTIVE)
            ->first();
    }

    /**
     * Static version used by Filament's canAccess() on pages and resources.
     */
    public static function currentMemberStatic(): ?AgencyMember
    {
        $agency = app()->bound('current_agency') ? app('current_agency') : null;
        $user = auth()->user();

        if (! $agency instanceof Agency || ! $user) {
            return null;
        }

        return AgencyMember::where('agency_id', $agency->id)
            ->where('user_id', $user->id)
            ->where('status', AgencyMember::STATUS_ACTIVE)
            ->first();
    }
}
