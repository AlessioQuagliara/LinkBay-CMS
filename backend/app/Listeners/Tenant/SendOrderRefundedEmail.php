<?php

declare(strict_types=1);

namespace App\Listeners\Tenant;

use App\Events\Tenant\OrderRefunded;
use App\Mail\Tenant\OrderRefundedMail;
use Illuminate\Support\Facades\Mail;

class SendOrderRefundedEmail
{
    public function handle(OrderRefunded $event): void
    {
        if (! $event->order->customer?->email) {
            return;
        }

        Mail::send(new OrderRefundedMail($event->order, $event->refundAmount));
    }
}
