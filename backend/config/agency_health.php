<?php

declare(strict_types=1);

/**
 * Thresholds for Agency Health classification.
 *
 * All counts are evaluated over the configurable window (default: 30 days).
 * Adjust these to fit your dataset as the platform grows.
 */
return [

    /*
    |--------------------------------------------------------------------------
    | Activity level — total events in the window
    |--------------------------------------------------------------------------
    */
    'activity' => [
        'high' => 50,  // >= 50 total events   → HIGH
        'medium' => 10,  // >= 10 total events    → MEDIUM, else LOW
    ],

    /*
    |--------------------------------------------------------------------------
    | Design usage — sum of panel design events:
    |   theme.preview_opened + theme.assigned + theme.fork_created + layout.saved
    |--------------------------------------------------------------------------
    */
    'design_usage' => [
        'high' => 10,  // >= 10 design events   → HIGH
        'medium' => 3,  // >=  3 design events   → MEDIUM, else LOW
    ],

    /*
    |--------------------------------------------------------------------------
    | Marketing usage — premium_block.rendered count in the window
    |--------------------------------------------------------------------------
    */
    'marketing_usage' => [
        'high' => 20,  // >= 20 renders → HIGH
        'medium' => 5,  // >=  5 renders → MEDIUM, else LOW
    ],

    /*
    |--------------------------------------------------------------------------
    | Premium adoption — requires active entitlements.
    |   None    = no active entitlements
    |   Partial = has entitlements but < 'good' threshold of premium renders
    |   Good    = has entitlements AND premium renders >= 'good' threshold
    |--------------------------------------------------------------------------
    */
    'premium_adoption' => [
        'good' => 5,  // premium_block.rendered + theme.rendered >= 5 → GOOD
    ],

    /*
    |--------------------------------------------------------------------------
    | Trend — compare current window vs previous window of same length.
    |   min_events: ignore trend when both windows are below this (too noisy)
    |   growth_pct: % increase to classify as GROWING
    |   decline_pct: % decrease to classify as DECLINING
    |--------------------------------------------------------------------------
    */
    'trend' => [
        'min_events' => 5,
        'growth_pct' => 20,
        'decline_pct' => 20,
    ],

];
