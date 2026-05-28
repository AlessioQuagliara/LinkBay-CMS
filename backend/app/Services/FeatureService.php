<?php

declare(strict_types=1);

namespace App\Services;

use App\Exceptions\FeatureNotAvailableException;
use App\Models\Central\Agency;

class FeatureService
{
    public function check(Agency $agency, string $feature): bool
    {
        // Lifetime plan uses its own rules, not overridden by billing_type
        return $agency->canUseFeature($feature);
    }

    public function enforce(Agency $agency, string $feature): void
    {
        if (!$this->check($agency, $feature)) {
            throw new FeatureNotAvailableException($feature);
        }
    }
}
