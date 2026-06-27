<?php

declare(strict_types=1);

namespace App\Contracts;

use App\Models\Tenant\Order;
use App\Models\Tenant\StorePaymentSettings;

interface StorePaymentServiceInterface
{
    /** @return array{client_secret: string, payment_intent_id: string} */
    public function createPaymentIntent(Order $order, ?string $customerId = null): array;

    public function capturePayment(Order $order): Order;

    public function refundOrder(Order $order, ?float $amount = null, ?string $reason = null): Order;

    public function getPaymentMethods(StorePaymentSettings $settings): array;
}
