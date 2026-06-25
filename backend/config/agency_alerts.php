<?php

declare(strict_types=1);

/**
 * Configuration for the Agency Early Warning system.
 *
 * Rules evaluate signals from AgencyHealthService and produce alerts
 * stored in agency_health_alerts. All thresholds and toggles are here —
 * no magic numbers in AgencyAlertService.
 */
return [

    /*
    |--------------------------------------------------------------------------
    | Default evaluation window (days)
    |--------------------------------------------------------------------------
    */
    'days_window_default' => 30,

    /*
    |--------------------------------------------------------------------------
    | Minimum days since a premium entitlement was granted before firing
    | the premium_not_used alert. Avoids noisy alerts for brand-new customers.
    |--------------------------------------------------------------------------
    */
    'min_days_since_premium' => 30,

    /*
    |--------------------------------------------------------------------------
    | Minimum total events in the current window required to fire design_drop.
    | Below this threshold the agency is too quiet to have a meaningful signal.
    |--------------------------------------------------------------------------
    */
    'min_events_for_design_alert' => 5,

    /*
    |--------------------------------------------------------------------------
    | Severity map — type => severity
    |--------------------------------------------------------------------------
    */
    'severity' => [
        'low_activity' => 'medium',
        'premium_not_used' => 'medium',
        'design_drop' => 'medium',
        'marketing_pack_inactive' => 'low',
    ],

    /*
    |--------------------------------------------------------------------------
    | Per-rule enable/disable toggles.
    | Set enabled = false to silence a rule globally without deleting code.
    |--------------------------------------------------------------------------
    */
    'rules' => [
        'low_activity' => ['enabled' => true],
        'premium_not_used' => ['enabled' => true],
        'design_drop' => ['enabled' => true],
        'marketing_pack_inactive' => ['enabled' => true],
    ],

];
