<?php

declare(strict_types=1);

namespace App\Console\Commands;

use App\Jobs\ProcessStripeWebhookJob;
use App\Models\Central\BillingEvent;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Log;

class ReprocessStuckBillingEvents extends Command
{
    protected $signature = 'billing:reprocess-stuck-events
                            {--minutes=15 : Riprocessa eventi non processati più vecchi di N minuti}
                            {--dry-run : Mostra gli eventi senza dispatchare i job}';

    protected $description = 'Riprocessa billing_events con processed_at = NULL più vecchi di N minuti';

    public function handle(): int
    {
        $minutes = (int) $this->option('minutes');
        $dryRun  = (bool) $this->option('dry-run');

        $stuck = BillingEvent::whereNull('processed_at')
            ->where('created_at', '<', now()->subMinutes($minutes))
            ->orderBy('created_at')
            ->get();

        if ($stuck->isEmpty()) {
            $this->info("Nessun billing_event bloccato (soglia: {$minutes} minuti).");
            return self::SUCCESS;
        }

        $this->warn("Trovati {$stuck->count()} eventi bloccati:");

        foreach ($stuck as $event) {
            $age = $event->created_at->diffForHumans();
            $this->line("  [{$event->id}] {$event->event_type} — {$age} — errore: " . ($event->error ?? 'nessuno'));

            if (!$dryRun) {
                ProcessStripeWebhookJob::dispatch($event->id);
            }
        }

        if ($dryRun) {
            $this->warn('Dry-run: nessun job dispatchato.');
        } else {
            $this->info("{$stuck->count()} job dispatchati.");
            Log::warning('billing:reprocess-stuck-events: dispatched jobs for stuck events', [
                'count'   => $stuck->count(),
                'minutes' => $minutes,
                'ids'     => $stuck->pluck('id')->toArray(),
            ]);
        }

        return self::SUCCESS;
    }
}
