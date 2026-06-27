<?php

declare(strict_types=1);

namespace App\Contracts;

use App\Models\Central\Agency;
use App\Models\Central\Plan;
use Illuminate\Support\Collection;

interface AgencyBillingServiceInterface
{
    public function createOrRetrieveCustomer(Agency $agency): string;

    public function startSubscription(
        Agency $agency,
        Plan $plan,
        string $paymentMethodId,
        string $interval = 'monthly',
    ): Agency;

    public function cancelSubscription(Agency $agency, bool $immediately = false): Agency;

    public function resumeSubscription(Agency $agency): Agency;

    public function changeSubscriptionPlan(Agency $agency, Plan $newPlan): Agency;

    /** @return array{amount_due: int, currency: string, next_payment_attempt: ?int, lines: array} */
    public function getUpcomingInvoice(Agency $agency): array;

    public function listInvoices(Agency $agency): Collection;

    public function updatePaymentMethod(Agency $agency, string $paymentMethodId): Agency;

    public function createSetupIntent(Agency $agency): string;

    public function syncSubscriptionFromStripe(Agency $agency, object $stripeSubscription): Agency;
}
