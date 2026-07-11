<?php

declare(strict_types=1);

namespace App\Services;

use App\Exceptions\AgencyPlanRequiredException;
use App\Models\Central\Agency;

/**
 * Single source of truth for "can this agency create a new store right now".
 *
 * Used identically by the agency-panel wizard (CreateStore) and the central
 * API (TenantController::store) so the business rule can't drift between the
 * two entry points.
 */
class StoreProvisioningGate
{
    public function check(Agency $agency): bool
    {
        return $agency->hasActivePlan();
    }

    public function enforce(Agency $agency): void
    {
        if (! $this->check($agency)) {
            throw new AgencyPlanRequiredException;
        }
    }
}
