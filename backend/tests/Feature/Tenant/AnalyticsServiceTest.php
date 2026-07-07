<?php

declare(strict_types=1);

namespace Tests\Feature\Tenant;

use App\Models\Tenant\Customer;
use App\Models\Tenant\Order;
use App\Services\Tenant\AnalyticsService;
use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\Cache;
use Tests\TenantTestCase;

class AnalyticsServiceTest extends TenantTestCase
{
    private AnalyticsService $analytics;

    private int $customerId;

    protected function setUp(): void
    {
        parent::setUp();
        $this->analytics = new AnalyticsService;
        Cache::flush();

        // Orders require a valid customer_id FK — create one for all order tests.
        $this->customerId = Customer::forceCreate([
            'name' => 'Test Customer',
            'email' => 'test@analytics.com',
            'created_at' => now(),
            'updated_at' => now(),
        ])->id;
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private function order(float $total, string $status, string $date): Order
    {
        return Order::forceCreate([
            'customer_id' => $this->customerId,
            'total' => $total,
            'subtotal' => $total,
            'status' => $status,
            'created_at' => $date,
            'updated_at' => $date,
        ]);
    }

    private function customer(string $name, string $email, string $date): Customer
    {
        return Customer::forceCreate([
            'name' => $name,
            'email' => $email,
            'created_at' => $date,
            'updated_at' => $date,
        ]);
    }

    // ── Tests ─────────────────────────────────────────────────────────────────

    public function test_get_revenue_total_sums_non_cancelled_orders(): void
    {
        $from = Carbon::parse('2026-01-01');
        $to = Carbon::parse('2026-01-31');

        $this->order(100.00, 'delivered', '2026-01-15');
        $this->order(50.00, 'cancelled', '2026-01-20');
        $this->order(75.00, 'confirmed', '2026-01-25');
        // Outside period — must be excluded
        $this->order(999.00, 'delivered', '2025-12-31');

        $total = $this->analytics->getRevenueTotal($from, $to);

        // 100 (delivered) + 75 (confirmed) = 175 — cancelled excluded
        $this->assertEqualsWithDelta(175.00, $total, 0.01);
    }

    public function test_get_revenue_total_returns_zero_when_no_orders(): void
    {
        $total = $this->analytics->getRevenueTotal(
            Carbon::parse('2026-01-01'),
            Carbon::parse('2026-01-31'),
        );

        $this->assertSame(0.0, $total);
    }

    public function test_get_revenue_total_excludes_refunded_orders(): void
    {
        $from = Carbon::parse('2026-02-01');
        $to = Carbon::parse('2026-02-28');

        $this->order(300.00, 'delivered', '2026-02-10');
        $this->order(100.00, 'refunded', '2026-02-15');

        $total = $this->analytics->getRevenueTotal($from, $to);

        $this->assertEqualsWithDelta(300.00, $total, 0.01);
    }

    public function test_get_orders_count(): void
    {
        $from = Carbon::parse('2026-03-01');
        $to = Carbon::parse('2026-03-31');

        $this->order(10.00, 'pending', '2026-03-10');
        $this->order(20.00, 'pending', '2026-03-20');
        $this->order(30.00, 'pending', '2026-02-28'); // outside

        $count = $this->analytics->getOrdersCount($from, $to);

        $this->assertSame(2, $count);
    }

    public function test_get_average_order_value(): void
    {
        $from = Carbon::parse('2026-04-01');
        $to = Carbon::parse('2026-04-30');

        $this->order(100.00, 'confirmed', '2026-04-10');
        $this->order(200.00, 'confirmed', '2026-04-20');

        $avg = $this->analytics->getAverageOrderValue($from, $to);

        $this->assertEqualsWithDelta(150.00, $avg, 0.01);
    }

    public function test_get_new_customers_count(): void
    {
        $from = Carbon::parse('2026-05-01');
        $to = Carbon::parse('2026-05-31');

        $this->customer('Alice', 'alice@test.com', '2026-05-10');
        $this->customer('Bob', 'bob@test.com', '2026-05-20');
        $this->customer('Old', 'old@test.com', '2026-04-30'); // outside

        // The setUp customer was created with now() (2026-07-02) — outside May range
        $count = $this->analytics->getNewCustomersCount($from, $to);

        $this->assertSame(2, $count);
    }

    public function test_compare_with_previous_period_detects_up_trend(): void
    {
        $from = Carbon::parse('2026-06-01');
        $to = Carbon::parse('2026-06-30');

        // Current period (Jun): 200
        $this->order(200.00, 'confirmed', '2026-06-15');
        // Previous period (May): 100
        $this->order(100.00, 'confirmed', '2026-05-15');

        $result = $this->analytics->compareWithPreviousPeriod('getRevenueTotal', $from, $to);

        $this->assertEqualsWithDelta(200.00, $result['current'], 0.01);
        $this->assertEqualsWithDelta(100.00, $result['previous'], 0.01);
        $this->assertSame('up', $result['trend']);
        $this->assertGreaterThan(0, $result['change_percent']);
    }

    public function test_compare_with_previous_period_detects_down_trend(): void
    {
        $from = Carbon::parse('2026-07-01');
        $to = Carbon::parse('2026-07-31');

        // Current period (Jul): 50
        $this->order(50.00, 'confirmed', '2026-07-10');
        // Previous period (Jun): 200
        $this->order(200.00, 'confirmed', '2026-06-10');

        $result = $this->analytics->compareWithPreviousPeriod('getRevenueTotal', $from, $to);

        $this->assertSame('down', $result['trend']);
        $this->assertLessThan(0, $result['change_percent']);
    }
}
