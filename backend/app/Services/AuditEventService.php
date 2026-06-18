<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Central\AuditEvent;

/**
 * Records append-only audit events.
 *
 * Caller is responsible for filtering sensitive data: never pass passwords,
 * tokens, or Stripe keys in old_values / new_values / metadata.
 */
class AuditEventService
{
    /**
     * Write one audit event record.
     *
     * Unresolved optional params fall back to the current HTTP context:
     *  - agency_id  → app('current_agency')?->id
     *  - user_id    → auth()->id()
     *  - ip_address → request()->ip() (null when running in queue / CLI)
     *
     * @param  array<string, mixed>|null  $oldValues  Relevant fields before change.
     * @param  array<string, mixed>|null  $newValues  Relevant fields after change.
     * @param  array<string, mixed>|null  $metadata  Contextual data (no secrets).
     */
    public function log(
        string $event,
        ?int $agencyId = null,
        ?int $userId = null,
        ?string $subjectType = null,
        int|string|null $subjectId = null,
        ?array $oldValues = null,
        ?array $newValues = null,
        ?array $metadata = null,
        ?string $ipAddress = null,
    ): AuditEvent {
        $agencyId ??= $this->resolveAgencyId();
        $userId ??= auth()->id();
        $ipAddress ??= $this->resolveIp();

        return AuditEvent::create([
            'agency_id' => $agencyId,
            'user_id' => $userId,
            'event' => $event,
            'subject_type' => $subjectType,
            'subject_id' => $subjectId !== null ? (string) $subjectId : null,
            'old_values' => $oldValues,
            'new_values' => $newValues,
            'ip_address' => $ipAddress,
            'metadata' => $metadata,
        ]);
    }

    private function resolveAgencyId(): ?int
    {
        try {
            $agency = app()->bound('current_agency') ? app('current_agency') : null;

            return $agency?->id;
        } catch (\Throwable) {
            return null;
        }
    }

    private function resolveIp(): ?string
    {
        try {
            if (app()->runningInConsole()) {
                return null;
            }

            return request()->ip();
        } catch (\Throwable) {
            return null;
        }
    }
}
