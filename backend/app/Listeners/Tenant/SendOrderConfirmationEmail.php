<?php

declare(strict_types=1);

namespace App\Listeners\Tenant;

use App\Events\Tenant\OrderPlaced;
use App\Mail\Tenant\NewOrderAdminMail;
use App\Mail\Tenant\OrderConfirmedMail;
use App\Models\Tenant\BrandSetting;
use App\Models\Tenant\User;
use Illuminate\Support\Facades\Mail;

class SendOrderConfirmationEmail
{
    public function handle(OrderPlaced $event): void
    {
        $order = $event->order;

        // Email to customer
        if ($order->customer?->email) {
            Mail::send(new OrderConfirmedMail($order));
        }

        // Email to admin users (role owner or with contact_email from brand)
        $brand = BrandSetting::current();
        $adminEmail = $brand->contact_email;

        if (! $adminEmail) {
            $adminEmail = User::where('role', User::ROLE_OWNER)->value('email');
        }

        if ($adminEmail) {
            Mail::send(new NewOrderAdminMail($order, $adminEmail));
        }
    }
}
