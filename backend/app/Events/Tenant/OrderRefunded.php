<?php

declare(strict_types=1);

namespace App\Events\Tenant;

use App\Models\Tenant\Order;
use Illuminate\Broadcasting\InteractsWithSockets;
use Illuminate\Foundation\Events\Dispatchable;
use Illuminate\Queue\SerializesModels;

class OrderRefunded
{
    use Dispatchable, InteractsWithSockets, SerializesModels;

    public function __construct(
        public readonly Order $order,
        public readonly float $refundAmount,
    ) {}
}
