<?php

declare(strict_types=1);

namespace App\Listeners\Tenant;

use App\Models\Tenant\OrderItem;
use App\Models\Tenant\User;
use App\Notifications\Tenant\LowStockNotification;
use Illuminate\Database\Eloquent\Events\Saved;

class CheckLowStock
{
    public function handle(Saved $event): void
    {
        if (! ($event->model instanceof OrderItem)) {
            return;
        }

        $orderItem = $event->model;
        $product = $orderItem->product;

        if (! $product) {
            return;
        }

        $qty = (int) $product->quantity;
        $threshold = (int) ($product->low_stock_threshold ?? 5);

        if ($qty <= $threshold) {
            $owners = User::where('role', User::ROLE_OWNER)->get();

            foreach ($owners as $user) {
                $user->notify(new LowStockNotification($product, $qty));
            }
        }
    }
}
