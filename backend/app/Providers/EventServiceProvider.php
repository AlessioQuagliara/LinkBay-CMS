<?php

declare(strict_types=1);

namespace App\Providers;

use App\Events\Tenant\CustomerRegistered;
use App\Events\Tenant\OrderPlaced;
use App\Events\Tenant\OrderRefunded;
use App\Events\Tenant\OrderShipped;
use App\Listeners\Tenant\NotifyAdminOfNewOrder;
use App\Listeners\Tenant\SendOrderConfirmationEmail;
use App\Listeners\Tenant\SendOrderRefundedEmail;
use App\Listeners\Tenant\SendOrderShippedEmail;
use App\Listeners\Tenant\SendWelcomeEmail;
use Illuminate\Database\Eloquent\Events\Saved;
use Illuminate\Foundation\Support\Providers\EventServiceProvider as ServiceProvider;

class EventServiceProvider extends ServiceProvider
{
    protected $listen = [
        OrderPlaced::class => [
            SendOrderConfirmationEmail::class,
            NotifyAdminOfNewOrder::class,
        ],
        OrderShipped::class => [
            SendOrderShippedEmail::class,
        ],
        OrderRefunded::class => [
            SendOrderRefundedEmail::class,
        ],
        CustomerRegistered::class => [
            SendWelcomeEmail::class,
        ],
    ];

    public function boot(): void
    {
        // Low-stock check via Eloquent model event (Saved on OrderItem)
        \App\Models\Tenant\OrderItem::saved(function (\App\Models\Tenant\OrderItem $item) {
            $event = new Saved($item);
            app(\App\Listeners\Tenant\CheckLowStock::class)->handle($event);
        });
    }
}
