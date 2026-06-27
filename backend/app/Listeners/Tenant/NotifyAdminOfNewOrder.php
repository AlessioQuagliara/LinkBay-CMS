<?php

declare(strict_types=1);

namespace App\Listeners\Tenant;

use App\Events\Tenant\OrderPlaced;
use App\Models\Tenant\User;
use App\Notifications\Tenant\NewOrderNotification;

class NotifyAdminOfNewOrder
{
    public function handle(OrderPlaced $event): void
    {
        $owners = User::where('role', User::ROLE_OWNER)->get();

        foreach ($owners as $user) {
            $user->notify(new NewOrderNotification($event->order));
        }
    }
}
