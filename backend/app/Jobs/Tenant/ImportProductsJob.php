<?php

declare(strict_types=1);

namespace App\Jobs\Tenant;

use App\Imports\Tenant\ProductImport;
use App\Models\Tenant\User;
use Filament\Notifications\Notification;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Storage;

class ImportProductsJob implements ShouldQueue
{
    use Dispatchable;
    use InteractsWithQueue;
    use Queueable;
    use SerializesModels;

    public int $timeout = 300;

    public int $tries = 1;

    /**
     * @param  string  $storagePath  Path relative to the default disk
     * @param  int  $notifiableUserId  Tenant user ID to notify on completion
     */
    public function __construct(
        private readonly string $storagePath,
        private readonly int $notifiableUserId,
    ) {}

    public function handle(ProductImport $importer): void
    {
        $absolutePath = Storage::path($this->storagePath);

        $importer->import($absolutePath, function (int $processed, int $total): void {
            $this->sendProgressNotification($processed, $total);
        });

        $this->sendCompletionNotification(
            $importer->createdCount(),
            $importer->updatedCount(),
            $importer->errors(),
        );

        Storage::delete($this->storagePath);
    }

    private function sendProgressNotification(int $processed, int $total): void
    {
        if ($total === 0 || $processed % 50 !== 0) {
            return;
        }

        Notification::make()
            ->title('Importazione in corso…')
            ->body("Elaborati {$processed} di {$total} prodotti.")
            ->info()
            ->sendToDatabase($this->resolveNotifiable());
    }

    /**
     * @param  list<array{row: int, error: string}>  $errors
     */
    private function sendCompletionNotification(int $created, int $updated, array $errors): void
    {
        $errorCount = count($errors);
        $body = "Creati: {$created} · Aggiornati: {$updated}";

        if ($errorCount > 0) {
            $body .= " · Errori: {$errorCount}";
        }

        Notification::make()
            ->title($errorCount > 0 ? 'Importazione completata con avvisi' : 'Importazione completata')
            ->body($body)
            ->when($errorCount > 0, fn ($n) => $n->warning(), fn ($n) => $n->success())
            ->sendToDatabase($this->resolveNotifiable());
    }

    private function resolveNotifiable(): User
    {
        return User::findOrFail($this->notifiableUserId);
    }

    public function failed(\Throwable $e): void
    {
        Notification::make()
            ->title('Importazione fallita')
            ->body($e->getMessage())
            ->danger()
            ->sendToDatabase($this->resolveNotifiable());

        Storage::delete($this->storagePath);
    }
}
