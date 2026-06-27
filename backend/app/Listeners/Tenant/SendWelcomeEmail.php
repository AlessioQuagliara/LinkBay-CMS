<?php

declare(strict_types=1);

namespace App\Listeners\Tenant;

use App\Events\Tenant\CustomerRegistered;
use App\Mail\Tenant\CustomerWelcomeMail;
use Illuminate\Support\Facades\Mail;

class SendWelcomeEmail
{
    public function handle(CustomerRegistered $event): void
    {
        Mail::send(new CustomerWelcomeMail($event->customer));
    }
}
