<?php

declare(strict_types=1);

namespace App\Notifications\Tenant;

use App\Models\Tenant\Order;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Notifications\Messages\BroadcastMessage;
use Illuminate\Notifications\Notification;

class NewOrderNotification extends Notification implements ShouldQueue
{
    use Queueable;

    public string $queue = 'default';

    public readonly string $orderNumber;

    public function __construct(public readonly Order $order)
    {
        $this->orderNumber = '#'.str_pad((string) $order->id, 4, '0', STR_PAD_LEFT);
        $this->order->loadMissing(['customer']);
    }

    public function via(object $notifiable): array
    {
        return ['database', 'broadcast'];
    }

    public function toDatabase(object $notifiable): array
    {
        $customerName = $this->order->customer?->name ?? 'Cliente';
        $total = '€'.number_format((float) $this->order->total, 2, ',', '.');

        return [
            'title' => "Nuovo ordine {$this->orderNumber}",
            'body' => "da {$customerName} — {$total}",
            'order_id' => $this->order->id,
            'url' => '/admin/orders/'.$this->order->id,
            'icon' => 'heroicon-o-shopping-cart',
            'color' => 'success',
        ];
    }

    public function toBroadcast(object $notifiable): BroadcastMessage
    {
        return new BroadcastMessage($this->toDatabase($notifiable));
    }
}
