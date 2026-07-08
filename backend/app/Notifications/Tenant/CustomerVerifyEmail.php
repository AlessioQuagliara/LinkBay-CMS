<?php

declare(strict_types=1);

namespace App\Notifications\Tenant;

use Illuminate\Auth\Notifications\VerifyEmail;
use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\URL;

/**
 * The default VerifyEmail notification signs a URL for the `verification.verify`
 * route, which doesn't exist for customers — their signed route is named
 * `customer.verification.verify` (see routes/tenant.php). Without this override,
 * every customer registration throws RouteNotFoundException.
 */
class CustomerVerifyEmail extends VerifyEmail
{
    protected function verificationUrl($notifiable): string
    {
        return URL::temporarySignedRoute(
            'customer.verification.verify',
            Carbon::now()->addMinutes(config('auth.verification.expire', 60)),
            [
                'id' => $notifiable->getKey(),
                'hash' => sha1($notifiable->getEmailForVerification()),
            ],
        );
    }
}
