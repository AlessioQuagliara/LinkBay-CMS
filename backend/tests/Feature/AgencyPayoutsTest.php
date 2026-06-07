<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Filament\Agency\Pages\PayoutsPage;
use App\Jobs\ProcessStripeWebhookJob;
use App\Models\Central\Agency;
use App\Models\Central\AgencyMember;
use App\Models\Central\BillingEvent;
use App\Models\Central\PayoutRecord;
use App\Models\Central\User;
use Tests\CentralTestCase;

/**
 * Covers the Payouts Visibility feature end-to-end.
 *
 * Tests:
 *  1.  payout.created event creates a PayoutRecord
 *  2.  payout.paid event updates status to paid (updateOrCreate)
 *  3.  payout.failed event sets failure_reason
 *  4.  payout.canceled maps to 'cancelled' status
 *  5.  Same Stripe payout ID is idempotent
 *  6.  Payout event with unknown Connect account is skipped
 *  7.  Payouts from different agencies are scoped correctly
 *  8.  BillingEvent.agency_id is stamped on resolution
 *  9.  Owner can access payouts page
 * 10.  Admin can access payouts page
 * 11.  Member cannot access payouts page
 * 12.  payouts() returns agency-scoped records
 * 13.  payouts() respects filterStatus
 * 14.  summaryStats() calculates correct totals
 */
class AgencyPayoutsTest extends CentralTestCase
{
    private static int $seq = 0;

    // ── Helpers ───────────────────────────────────────────────────────────────

    private function makeAgency(string $connectAccountId = ''): Agency
    {
        self::$seq++;

        $agency = Agency::create([
            'name' => 'Agency '.self::$seq,
            'slug' => 'agency-'.self::$seq,
            'brand_name' => 'Agency '.self::$seq,
            'status' => 'active',
            'billing_type' => 'monthly',
            'stripe_connect_onboarded' => (bool) $connectAccountId,
        ]);

        if ($connectAccountId) {
            $agency->update(['stripe_connect_account_id' => $connectAccountId]);
        }

        return $agency;
    }

    private function makeUser(Agency $agency, string $role): User
    {
        self::$seq++;

        $user = User::create([
            'name' => 'User '.self::$seq,
            'email' => 'user'.self::$seq.'@example.com',
            'password' => bcrypt('password'),
        ]);

        AgencyMember::create([
            'agency_id' => $agency->id,
            'user_id' => $user->id,
            'role' => $role,
            'status' => AgencyMember::STATUS_ACTIVE,
            'accepted_at' => now(),
        ]);

        return $user;
    }

    private function makePage(Agency $agency): PayoutsPage
    {
        app()->instance('current_agency', $agency);

        return app(PayoutsPage::class);
    }

    /**
     * Builds a BillingEvent whose payload mimics a Stripe payout.* Connect event.
     */
    private function makeBillingEvent(
        string $eventType,
        string $connectAccountId,
        string $stripePayoutId = 'po_test',
        string $status = 'paid',
        int $amountCents = 10000,
        string $currency = 'eur',
        ?string $failureMessage = null,
    ): BillingEvent {
        return BillingEvent::create([
            'stripe_event_id' => 'evt_'.uniqid(),
            'event_type' => $eventType,
            'payload' => [
                'account' => $connectAccountId,
                'data' => [
                    'object' => [
                        'id' => $stripePayoutId,
                        'object' => 'payout',
                        'amount' => $amountCents,
                        'currency' => $currency,
                        'status' => $status,
                        'arrival_date' => now()->addDays(3)->timestamp,
                        'failure_message' => $failureMessage,
                        'metadata' => [],
                    ],
                ],
            ],
        ]);
    }

    private function dispatchJob(BillingEvent $event): void
    {
        ProcessStripeWebhookJob::dispatchSync($event->id);
    }

    // ── Webhook job tests ─────────────────────────────────────────────────────

    public function test_payout_created_event_creates_payout_record(): void
    {
        $agency = $this->makeAgency('acct_t1');
        $event = $this->makeBillingEvent('payout.created', 'acct_t1', 'po_001', 'pending', 5000);

        $this->dispatchJob($event);

        $this->assertDatabaseHas('payout_records', [
            'agency_id' => $agency->id,
            'stripe_payout_id' => 'po_001',
            'status' => PayoutRecord::STATUS_PENDING,
            'amount_cents' => 5000,
            'currency' => 'eur',
        ], 'central');
    }

    public function test_payout_paid_event_updates_existing_record(): void
    {
        $agency = $this->makeAgency('acct_t2');

        $this->dispatchJob($this->makeBillingEvent('payout.created', 'acct_t2', 'po_002', 'in_transit'));
        $this->dispatchJob($this->makeBillingEvent('payout.paid', 'acct_t2', 'po_002', 'paid'));

        $this->assertDatabaseHas('payout_records', [
            'stripe_payout_id' => 'po_002',
            'status' => PayoutRecord::STATUS_PAID,
        ], 'central');
        $this->assertEquals(1, PayoutRecord::where('stripe_payout_id', 'po_002')->count(), 'No duplicate records');
    }

    public function test_payout_failed_event_sets_failure_reason(): void
    {
        $agency = $this->makeAgency('acct_t3');
        $event = $this->makeBillingEvent('payout.failed', 'acct_t3', 'po_003', 'failed', 3000, 'eur', 'Account cannot be used for payouts');

        $this->dispatchJob($event);

        $record = PayoutRecord::where('stripe_payout_id', 'po_003')->firstOrFail();
        $this->assertEquals(PayoutRecord::STATUS_FAILED, $record->status);
        $this->assertEquals('Account cannot be used for payouts', $record->failure_reason);
    }

    public function test_payout_canceled_maps_to_cancelled_status(): void
    {
        $agency = $this->makeAgency('acct_t4');
        $this->dispatchJob($this->makeBillingEvent('payout.canceled', 'acct_t4', 'po_004', 'canceled'));

        $this->assertDatabaseHas('payout_records', [
            'stripe_payout_id' => 'po_004',
            'status' => PayoutRecord::STATUS_CANCELLED,
        ], 'central');
    }

    public function test_same_payout_id_is_idempotent(): void
    {
        $agency = $this->makeAgency('acct_t5');

        $this->dispatchJob($this->makeBillingEvent('payout.created', 'acct_t5', 'po_005', 'pending'));
        $this->dispatchJob($this->makeBillingEvent('payout.paid', 'acct_t5', 'po_005', 'paid'));

        $this->assertEquals(1, PayoutRecord::where('stripe_payout_id', 'po_005')->count());
        $this->assertEquals(PayoutRecord::STATUS_PAID, PayoutRecord::where('stripe_payout_id', 'po_005')->value('status'));
    }

    public function test_payout_event_with_unknown_connect_account_is_skipped(): void
    {
        $event = $this->makeBillingEvent('payout.paid', 'acct_unknown_xyz', 'po_006', 'paid');

        $this->dispatchJob($event);

        $this->assertEquals(0, PayoutRecord::where('stripe_payout_id', 'po_006')->count());
    }

    public function test_payouts_are_scoped_to_correct_agency(): void
    {
        $agencyA = $this->makeAgency('acct_A01');
        $agencyB = $this->makeAgency('acct_B01');

        $this->dispatchJob($this->makeBillingEvent('payout.paid', 'acct_A01', 'po_A01', 'paid'));
        $this->dispatchJob($this->makeBillingEvent('payout.paid', 'acct_B01', 'po_B01', 'paid'));

        $this->assertEquals(1, PayoutRecord::where('agency_id', $agencyA->id)->count());
        $this->assertEquals(1, PayoutRecord::where('agency_id', $agencyB->id)->count());
        $this->assertEquals($agencyA->id, PayoutRecord::where('stripe_payout_id', 'po_A01')->value('agency_id'));
        $this->assertEquals($agencyB->id, PayoutRecord::where('stripe_payout_id', 'po_B01')->value('agency_id'));
    }

    public function test_billing_event_agency_id_is_stamped_on_resolution(): void
    {
        $agency = $this->makeAgency('acct_stamp1');
        $event = $this->makeBillingEvent('payout.paid', 'acct_stamp1', 'po_stamp', 'paid');

        $this->assertNull($event->agency_id);

        $this->dispatchJob($event);

        $event->refresh();
        $this->assertEquals($agency->id, $event->agency_id);
    }

    // ── Page access control ───────────────────────────────────────────────────

    public function test_owner_can_access_payouts_page(): void
    {
        $agency = $this->makeAgency();
        $owner = $this->makeUser($agency, AgencyMember::ROLE_OWNER);

        app()->instance('current_agency', $agency);
        $this->actingAs($owner, 'web');

        $this->assertTrue(PayoutsPage::canAccess());
    }

    public function test_admin_can_access_payouts_page(): void
    {
        $agency = $this->makeAgency();
        $admin = $this->makeUser($agency, AgencyMember::ROLE_ADMIN);

        app()->instance('current_agency', $agency);
        $this->actingAs($admin, 'web');

        $this->assertTrue(PayoutsPage::canAccess());
    }

    public function test_member_cannot_access_payouts_page(): void
    {
        $agency = $this->makeAgency();
        $member = $this->makeUser($agency, AgencyMember::ROLE_MEMBER);

        app()->instance('current_agency', $agency);
        $this->actingAs($member, 'web');

        $this->assertFalse(PayoutsPage::canAccess());
    }

    // ── Page data methods ─────────────────────────────────────────────────────

    public function test_payouts_returns_agency_scoped_records(): void
    {
        $agencyA = $this->makeAgency('acct_scope1');
        $agencyB = $this->makeAgency('acct_scope2');

        PayoutRecord::create(['agency_id' => $agencyA->id, 'stripe_payout_id' => 'po_sc1', 'amount_cents' => 1000, 'currency' => 'eur', 'status' => 'paid',    'stripe_connect_account_id' => 'acct_scope1']);
        PayoutRecord::create(['agency_id' => $agencyB->id, 'stripe_payout_id' => 'po_sc2', 'amount_cents' => 2000, 'currency' => 'eur', 'status' => 'paid',    'stripe_connect_account_id' => 'acct_scope2']);

        $page = $this->makePage($agencyA);
        $result = $page->payouts();

        $this->assertCount(1, $result);
        $this->assertEquals('po_sc1', $result->first()->stripe_payout_id);
    }

    public function test_payouts_filtered_by_status(): void
    {
        $agency = $this->makeAgency('acct_flt1');

        PayoutRecord::create(['agency_id' => $agency->id, 'stripe_payout_id' => 'po_fl1', 'amount_cents' => 1000, 'currency' => 'eur', 'status' => 'paid',    'stripe_connect_account_id' => 'acct_flt1']);
        PayoutRecord::create(['agency_id' => $agency->id, 'stripe_payout_id' => 'po_fl2', 'amount_cents' => 2000, 'currency' => 'eur', 'status' => 'pending', 'stripe_connect_account_id' => 'acct_flt1']);

        $page = $this->makePage($agency);
        $page->filterStatus = 'paid';

        $result = $page->payouts();

        $this->assertCount(1, $result);
        $this->assertEquals('po_fl1', $result->first()->stripe_payout_id);
    }

    public function test_summary_stats_calculates_correct_totals(): void
    {
        $agency = $this->makeAgency('acct_sum1');

        PayoutRecord::create(['agency_id' => $agency->id, 'stripe_payout_id' => 'po_sum1', 'amount_cents' => 50000, 'currency' => 'eur', 'status' => 'paid',       'stripe_connect_account_id' => 'acct_sum1']);
        PayoutRecord::create(['agency_id' => $agency->id, 'stripe_payout_id' => 'po_sum2', 'amount_cents' => 10000, 'currency' => 'eur', 'status' => 'in_transit', 'stripe_connect_account_id' => 'acct_sum1']);
        PayoutRecord::create(['agency_id' => $agency->id, 'stripe_payout_id' => 'po_sum3', 'amount_cents' => 5000,  'currency' => 'eur', 'status' => 'failed',     'stripe_connect_account_id' => 'acct_sum1']);

        $page = $this->makePage($agency);
        $stats = $page->summaryStats();

        $this->assertEquals(50000, $stats['paid_cents']);
        $this->assertEquals(10000, $stats['in_transit_cents']);
        $this->assertEquals(0, $stats['pending_cents']);
        $this->assertEquals(1, $stats['failed_count']);
    }
}
