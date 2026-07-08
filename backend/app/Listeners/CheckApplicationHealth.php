<?php

declare(strict_types=1);

namespace App\Listeners;

use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Redis;
use RuntimeException;

/**
 * Extends the built-in /up healthcheck (bootstrap/app.php `health: '/up'`) beyond
 * "the framework booted". Any exception thrown here turns /up into a 500, which is
 * what staging/production uptime monitors (UptimeRobot, curl in CI, etc.) should watch.
 */
class CheckApplicationHealth
{
    public function handle(): void
    {
        try {
            DB::connection('central')->getPdo();
        } catch (\Throwable $e) {
            throw new RuntimeException('Central database unreachable: '.$e->getMessage(), previous: $e);
        }

        try {
            Redis::connection()->ping();
        } catch (\Throwable $e) {
            throw new RuntimeException('Redis unreachable: '.$e->getMessage(), previous: $e);
        }
    }
}
