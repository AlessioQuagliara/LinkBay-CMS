<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\Agency;
use App\Models\Central\AiCreditLedger;
use App\Services\AiCreditsService;
use Illuminate\Support\Facades\DB;
use Tests\CentralTestCase;

/**
 * Covers AiCreditsService::storeBreakdown() — per-store AI credit usage.
 *
 * Tests:
 *  1.  Only the current agency's consumption records are included
 *  2.  Credits are summed correctly per store
 *  3.  Event count is accurate per store
 *  4.  Stores are ordered by highest consumption first
 *  5.  Records with null tenant_id are labelled "Sistema"
 *  6.  Purchase/bonus entries are excluded (only consumption counts)
 *  7.  Empty collection when agency has no consumption
 *  8.  Deleted store (tenant_id not in tenants table) gets fallback name
 *  9.  Date filter: only records within range are included
 * 10.  Date filter: null (all-time) returns all records
 * 11.  last_used_at reflects the most recent consumption for that store
 * 12.  Totals across all rows sum correctly
 */
class AiCreditsUsageServiceTest extends CentralTestCase
{
    private static int $seq = 0;

    // ── Helpers ───────────────────────────────────────────────────────────────

    private function makeAgency(): Agency
    {
        self::$seq++;

        return Agency::create([
            'name' => 'Agency '.self::$seq,
            'slug' => 'agency-'.self::$seq,
            'brand_name' => 'Agency '.self::$seq,
            'status' => 'active',
            'billing_type' => 'monthly',
        ]);
    }

    /**
     * Insert a tenant row directly to avoid stancl/tenancy DB-provisioning hooks.
     */
    private function addStore(Agency $agency, string $name): string
    {
        self::$seq++;
        $id = 'store-'.self::$seq;

        DB::connection('central')->table('tenants')->insert([
            'id' => $id,
            'name' => $name,
            'status' => 'active',
            'agency_id' => $agency->id,
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        return $id;
    }

    private function consume(Agency $agency, ?string $tenantId, int $credits, ?string $createdAt = null): void
    {
        AiCreditLedger::create([
            'agency_id' => $agency->id,
            'tenant_id' => $tenantId,
            'amount' => -$credits,
            'balance_after' => 0,
            'type' => AiCreditLedger::TYPE_CONSUMPTION,
            'description' => 'Test consumption',
            'created_at' => $createdAt ?? now(),
        ]);
    }

    private function addNonConsumption(Agency $agency, ?string $tenantId, int $amount, string $type): void
    {
        AiCreditLedger::create([
            'agency_id' => $agency->id,
            'tenant_id' => $tenantId,
            'amount' => $amount,
            'balance_after' => $amount,
            'type' => $type,
            'description' => "Test {$type}",
            'created_at' => now(),
        ]);
    }

    private function service(): AiCreditsService
    {
        return app(AiCreditsService::class);
    }

    // ── Agency scoping ────────────────────────────────────────────────────────

    public function test_only_current_agency_consumption_is_included(): void
    {
        $agencyA = $this->makeAgency();
        $agencyB = $this->makeAgency();
        $storeA = $this->addStore($agencyA, 'Store A');
        $storeB = $this->addStore($agencyB, 'Store B');

        $this->consume($agencyA, $storeA, 100);
        $this->consume($agencyB, $storeB, 200);

        $breakdown = $this->service()->storeBreakdown($agencyA);

        $this->assertCount(1, $breakdown);
        $this->assertEquals($storeA, $breakdown->first()->tenant_id);
        $this->assertEquals(100, $breakdown->first()->credits_consumed);
    }

    // ── Grouping and summing ──────────────────────────────────────────────────

    public function test_credits_are_summed_per_store(): void
    {
        $agency = $this->makeAgency();
        $store = $this->addStore($agency, 'My Store');

        $this->consume($agency, $store, 50);
        $this->consume($agency, $store, 30);
        $this->consume($agency, $store, 20);

        $breakdown = $this->service()->storeBreakdown($agency);

        $this->assertCount(1, $breakdown);
        $this->assertEquals(100, $breakdown->first()->credits_consumed);
    }

    public function test_event_count_is_accurate_per_store(): void
    {
        $agency = $this->makeAgency();
        $store = $this->addStore($agency, 'My Store');

        $this->consume($agency, $store, 10);
        $this->consume($agency, $store, 10);
        $this->consume($agency, $store, 10);

        $breakdown = $this->service()->storeBreakdown($agency);

        $this->assertEquals(3, $breakdown->first()->event_count);
    }

    public function test_multiple_stores_grouped_separately(): void
    {
        $agency = $this->makeAgency();
        $storeA = $this->addStore($agency, 'Alpha');
        $storeB = $this->addStore($agency, 'Beta');

        $this->consume($agency, $storeA, 70);
        $this->consume($agency, $storeB, 30);

        $breakdown = $this->service()->storeBreakdown($agency);

        $this->assertCount(2, $breakdown);

        $byId = $breakdown->keyBy('tenant_id');
        $this->assertEquals(70, $byId->get($storeA)->credits_consumed);
        $this->assertEquals(30, $byId->get($storeB)->credits_consumed);
    }

    // ── Ordering ──────────────────────────────────────────────────────────────

    public function test_stores_ordered_by_highest_consumption_first(): void
    {
        $agency = $this->makeAgency();
        $low = $this->addStore($agency, 'Low');
        $high = $this->addStore($agency, 'High');

        $this->consume($agency, $low, 10);
        $this->consume($agency, $high, 500);

        $breakdown = $this->service()->storeBreakdown($agency);

        $this->assertEquals($high, $breakdown->first()->tenant_id);
        $this->assertEquals($low, $breakdown->last()->tenant_id);
    }

    // ── Unattributed (null tenant_id) ─────────────────────────────────────────

    public function test_null_tenant_id_is_labelled_sistema(): void
    {
        $agency = $this->makeAgency();
        $this->consume($agency, null, 50);

        $breakdown = $this->service()->storeBreakdown($agency);

        $this->assertCount(1, $breakdown);
        $this->assertNull($breakdown->first()->tenant_id);
        $this->assertEquals('Sistema', $breakdown->first()->store_name);
    }

    // ── Non-consumption entries excluded ─────────────────────────────────────

    public function test_purchase_and_bonus_entries_are_excluded(): void
    {
        $agency = $this->makeAgency();
        $store = $this->addStore($agency, 'My Store');

        $this->addNonConsumption($agency, $store, 500, AiCreditLedger::TYPE_PURCHASE);
        $this->addNonConsumption($agency, $store, 100, AiCreditLedger::TYPE_BONUS);

        $breakdown = $this->service()->storeBreakdown($agency);

        $this->assertCount(0, $breakdown, 'Purchases and bonuses must not appear in the consumption breakdown');
    }

    // ── Empty states ──────────────────────────────────────────────────────────

    public function test_empty_collection_when_no_consumption(): void
    {
        $agency = $this->makeAgency();

        $breakdown = $this->service()->storeBreakdown($agency);

        $this->assertTrue($breakdown->isEmpty());
    }

    public function test_empty_collection_when_only_purchases_exist(): void
    {
        $agency = $this->makeAgency();
        $this->addNonConsumption($agency, null, 1000, AiCreditLedger::TYPE_PURCHASE);

        $breakdown = $this->service()->storeBreakdown($agency);

        $this->assertTrue($breakdown->isEmpty());
    }

    // ── Deleted store fallback ────────────────────────────────────────────────

    public function test_deleted_store_gets_fallback_name(): void
    {
        $agency = $this->makeAgency();
        // Reference a tenant_id that does not exist in the tenants table
        $ghostId = 'ghost-store-that-was-deleted';

        $this->consume($agency, $ghostId, 75);

        $breakdown = $this->service()->storeBreakdown($agency);

        $this->assertCount(1, $breakdown);
        $this->assertEquals("Store #{$ghostId}", $breakdown->first()->store_name);
    }

    // ── Date filter ───────────────────────────────────────────────────────────

    public function test_date_filter_excludes_records_before_since(): void
    {
        $agency = $this->makeAgency();
        $store = $this->addStore($agency, 'My Store');

        // Old consumption (61 days ago)
        $this->consume($agency, $store, 200, now()->subDays(61)->toDateTimeString());
        // Recent consumption (within 30 days)
        $this->consume($agency, $store, 50, now()->subDays(5)->toDateTimeString());

        $breakdown = $this->service()->storeBreakdown($agency, since: now()->subDays(30));

        $this->assertCount(1, $breakdown);
        $this->assertEquals(50, $breakdown->first()->credits_consumed);
    }

    public function test_null_since_returns_all_records(): void
    {
        $agency = $this->makeAgency();
        $store = $this->addStore($agency, 'My Store');

        $this->consume($agency, $store, 200, now()->subDays(200)->toDateTimeString());
        $this->consume($agency, $store, 50, now()->subDays(5)->toDateTimeString());

        $breakdown = $this->service()->storeBreakdown($agency, since: null);

        $this->assertEquals(250, $breakdown->first()->credits_consumed);
    }

    public function test_date_filter_returns_empty_when_all_records_are_old(): void
    {
        $agency = $this->makeAgency();
        $store = $this->addStore($agency, 'My Store');

        $this->consume($agency, $store, 100, now()->subDays(60)->toDateTimeString());

        $breakdown = $this->service()->storeBreakdown($agency, since: now()->subDays(30));

        $this->assertTrue($breakdown->isEmpty());
    }

    // ── last_used_at ──────────────────────────────────────────────────────────

    public function test_last_used_at_reflects_most_recent_consumption(): void
    {
        $agency = $this->makeAgency();
        $store = $this->addStore($agency, 'My Store');

        $this->consume($agency, $store, 10, now()->subDays(10)->toDateTimeString());
        $this->consume($agency, $store, 10, now()->subDays(2)->toDateTimeString());
        $this->consume($agency, $store, 10, now()->subDays(5)->toDateTimeString());

        $breakdown = $this->service()->storeBreakdown($agency);

        // last_used_at should be the most recent (2 days ago), within ±1 minute margin
        $this->assertNotNull($breakdown->first()->last_used_at);
        $this->assertTrue(
            $breakdown->first()->last_used_at->gte(now()->subDays(3)),
            'last_used_at should be ~2 days ago'
        );
    }

    // ── Total sanity ─────────────────────────────────────────────────────────

    public function test_total_credits_across_all_stores_is_correct(): void
    {
        $agency = $this->makeAgency();
        $storeA = $this->addStore($agency, 'A');
        $storeB = $this->addStore($agency, 'B');

        $this->consume($agency, $storeA, 100);
        $this->consume($agency, $storeA, 50);
        $this->consume($agency, $storeB, 200);

        $breakdown = $this->service()->storeBreakdown($agency);

        $this->assertEquals(350, $breakdown->sum('credits_consumed'));
    }
}
