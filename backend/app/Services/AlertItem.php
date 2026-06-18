<?php

declare(strict_types=1);

namespace App\Services;

/**
 * Immutable value object representing a single operational alert for the Agency dashboard.
 */
readonly class AlertItem
{
    public function __construct(
        /** Stable key used for deduplication and testing. */
        public string $key,
        /** 'danger' | 'warning' | 'info' */
        public string $severity,
        public string $title,
        public string $body,
        public string $ctaLabel,
        /** Named route for the CTA link. */
        public string $ctaRoute,
        /** Lower number = displayed first. */
        public int $priority,
        /**
         * When true, the CTA resolves to a page only owners can access.
         * The view renders a "Contact your owner" note for non-owners instead.
         */
        public bool $ctaOwnerOnly = false,
    ) {}
}
