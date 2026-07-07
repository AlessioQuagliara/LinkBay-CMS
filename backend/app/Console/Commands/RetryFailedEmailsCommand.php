<?php

declare(strict_types=1);

namespace App\Console\Commands;

use Illuminate\Console\Command;
use Illuminate\Support\Facades\DB;

class RetryFailedEmailsCommand extends Command
{
    protected $signature = 'emails:retry-failed
                            {--hours=24 : Only retry jobs failed within the last N hours}';

    protected $description = 'Retry failed email jobs from the emails queue.';

    public function handle(): int
    {
        $hours = (int) $this->option('hours');
        $since = now()->subHours($hours);

        $jobs = DB::table('failed_jobs')
            ->where('queue', 'emails')
            ->where('failed_at', '>=', $since)
            ->pluck('uuid');

        if ($jobs->isEmpty()) {
            $this->info('No failed email jobs in the last '.$hours.' hour(s).');

            return self::SUCCESS;
        }

        $this->info("Retrying {$jobs->count()} failed email job(s)…");

        $retried = 0;
        $failed = 0;

        foreach ($jobs as $uuid) {
            $exitCode = $this->call('queue:retry', ['id' => [$uuid]]);

            if ($exitCode === 0) {
                $retried++;
            } else {
                $failed++;
                $this->warn("Could not retry job {$uuid}.");
            }
        }

        $this->info("Done — retried: {$retried}, errors: {$failed}.");

        return $failed > 0 ? self::FAILURE : self::SUCCESS;
    }
}
