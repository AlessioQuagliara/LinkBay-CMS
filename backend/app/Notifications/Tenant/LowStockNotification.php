<?php

declare(strict_types=1);

namespace App\Notifications\Tenant;

use App\Models\Tenant\Product;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Notifications\Notification;

class LowStockNotification extends Notification implements ShouldQueue
{
    use Queueable;

    public string $queue = 'default';

    public function __construct(
        public readonly Product $product,
        public readonly int $currentQty,
    ) {}

    public function via(object $notifiable): array
    {
        return ['database'];
    }

    public function toDatabase(object $notifiable): array
    {
        return [
            'title' => 'Scorte basse: '.$this->product->name,
            'body' => "Solo {$this->currentQty} unità rimaste (soglia: {$this->product->low_stock_threshold})",
            'product_id' => $this->product->id,
            'url' => '/admin/products/'.$this->product->id.'/edit',
            'icon' => 'heroicon-o-exclamation-triangle',
            'color' => 'warning',
        ];
    }
}
