<?php

declare(strict_types=1);

namespace App\Console\Commands;

use App\Services\AgencyAlertService;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Log;

class EvaluateHealthAlerts extends Command
{
    protected $signature = 'agency:health-alerts {--days=30 : Evaluation window in days}';

    protected $description = 'Evaluate health rules for all agencies and create early-warning alerts.';

    public function handle(AgencyAlertService $svc): int
    {
        $days = (int) $this->option('days');

        $this->info("Evaluating agency health alerts (window: {$days} days)…");

        $created = $svc->evaluateAndStoreAlerts($days);

        $total = (int) array_sum($created);

        if ($total === 0) {
            $this->info('No new alerts.');
        } else {
            $this->info("{$total} new alert(s) created:");
            foreach ($created as $type => $count) {
                $this->line("  • {$type}: {$count}");
            }
        }

        Log::info('agency:health-alerts completed', [
            'days' => $days,
            'created' => $created,
            'total' => $total,
        ]);

        return self::SUCCESS;
    }
}
