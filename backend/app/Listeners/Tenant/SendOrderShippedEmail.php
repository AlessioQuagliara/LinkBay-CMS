<?php

declare(strict_types=1);

namespace App\Listeners\Tenant;

use App\Events\Tenant\OrderShipped;
use App\Mail\Tenant\OrderShippedMail;
use Illuminate\Support\Facades\Mail;

class SendOrderShippedEmail
{
    public function handle(OrderShipped $event): void
    {
        if (! $event->order->customer?->email) {
            return;
        }

        Mail::send(new OrderShippedMail(
            $event->order,
            $event->trackingNumber,
            $event->carrierName,
            $event->trackingUrl,
        ));
    }
}
