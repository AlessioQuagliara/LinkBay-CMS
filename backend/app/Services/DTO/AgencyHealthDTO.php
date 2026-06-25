<?php

declare(strict_types=1);

namespace App\Services\DTO;

use App\Enums\ActivityLevel;
use App\Enums\PremiumAdoptionLevel;
use App\Enums\TrendDirection;
use App\Enums\UsageLevel;

/**
 * Immutable snapshot of an agency's health for a given time window.
 *
 * Classification fields (activityLevel etc.) are derived by AgencyHealthService
 * from the raw numeric fields below, using thresholds from config/agency_health.php.
 */
final class AgencyHealthDTO
{
    public function __construct(
        public readonly int $agencyId,
        public readonly string $agencyName,
        /** Window length in days (7 / 30 / 90). */
        public readonly int $windowDays,

        // ── Classified indicators ─────────────────────────────────────────────
        public readonly ActivityLevel $activityLevel,
        public readonly UsageLevel $designUsageLevel,
        public readonly UsageLevel $marketingUsageLevel,
        public readonly PremiumAdoptionLevel $premiumAdoptionLevel,
        public readonly TrendDirection $trend,

        // ── Raw counts ────────────────────────────────────────────────────────
        public readonly int $totalEvents,
        public readonly int $activeTenants,
        public readonly int $daysActive,
        public readonly int $previewCount,
        public readonly int $themeAssignedCount,
        public readonly int $forkCount,
        public readonly int $layoutSavedCount,
        public readonly int $premiumBlockRenders,
        public readonly int $premiumThemeRenders,
        public readonly int $activeEntitlementCount,
    ) {}
}
