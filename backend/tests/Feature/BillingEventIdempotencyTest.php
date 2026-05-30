<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\BillingEvent;
use Tests\CentralTestCase;

class BillingEventIdempotencyTest extends CentralTestCase
{
    public function test_insertOrIgnore_does_not_create_duplicate_on_same_stripe_event_id(): void
    {
        $eventId = 'evt_test_' . uniqid();

        $count1 = BillingEvent::insertOrIgnore([
            'stripe_event_id' => $eventId,
            'event_type'      => 'payment_intent.succeeded',
            'payload'         => json_encode(['data' => ['object' => []]]),
            'created_at'      => now(),
        ]);

        $count2 = BillingEvent::insertOrIgnore([
            'stripe_event_id' => $eventId,
            'event_type'      => 'payment_intent.succeeded',
            'payload'         => json_encode(['data' => ['object' => []]]),
            'created_at'      => now(),
        ]);

        $this->assertEquals(1, $count1, 'Primo inserimento deve creare 1 riga');
        $this->assertEquals(0, $count2, 'Secondo inserimento deve essere ignorato');
        $this->assertEquals(1, BillingEvent::where('stripe_event_id', $eventId)->count());
    }

    public function test_billing_event_is_marked_processed(): void
    {
        $event = BillingEvent::create([
            'stripe_event_id' => 'evt_test_' . uniqid(),
            'event_type'      => 'account.updated',
            'payload'         => ['data' => ['object' => []]],
        ]);

        $this->assertFalse($event->isProcessed());

        $event->markProcessed();
        $event->refresh();

        $this->assertTrue($event->isProcessed());
        $this->assertNotNull($event->processed_at);
    }

    public function test_billing_event_saves_error_on_failure(): void
    {
        $event = BillingEvent::create([
            'stripe_event_id' => 'evt_err_' . uniqid(),
            'event_type'      => 'checkout.session.completed',
            'payload'         => ['data' => ['object' => []]],
        ]);

        $event->markFailed('Agency not found for customer cus_xxx');
        $event->refresh();

        $this->assertEquals('Agency not found for customer cus_xxx', $event->error);
        $this->assertFalse($event->isProcessed(), 'markFailed non deve impostare processed_at');
    }
}
