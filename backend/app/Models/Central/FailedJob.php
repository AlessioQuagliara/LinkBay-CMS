<?php

declare(strict_types=1);

namespace App\Models\Central;

use Illuminate\Database\Eloquent\Model;

/**
 * Read model over Laravel's own `failed_jobs` table. No new storage — this just
 * gives the Admin panel visibility into jobs that queue:work already recorded as
 * failed (webhook processing, tenant provisioning, etc.), which otherwise only
 * exist in a table nobody looks at.
 */
class FailedJob extends Model
{
    protected $connection = 'central';

    protected $table = 'failed_jobs';

    public $timestamps = false;

    protected $casts = [
        'failed_at' => 'datetime',
    ];

    public function jobClass(): string
    {
        $payload = json_decode($this->payload, true);

        return $payload['displayName'] ?? 'unknown';
    }

    public function exceptionSummary(): string
    {
        return strtok($this->exception, "\n") ?: $this->exception;
    }
}
