<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Filament\Agency\Widgets\AgencyStatsWidget;
use App\Models\Central\Agency;
use App\Models\Central\CommissionRecord;
use App\Models\Central\PlatformFeeRule;
use Illuminate\Support\Carbon;
use Tests\CentralTestCase;

/**
 * Covers AgencyStatsWidget::monthlyRevenue() — the new "Ricavi netti" stat.
 *
 * Each test verifies one behavioural boundary:
 *   1. Zero when the agency has no CommissionRecords.
 *   2. Only STATUS_SETTLED records are included.
 *   3. Only records in the current calendar month are included.
 *   4. Records from a different agency are excluded.
 *   5. Both net and gross totals are correct, and the count matches.
 */
class AgencyDashboardStatsTest extends CentralTestCase
{
    // ── Helpers ───────────────────────────────────────────────────────────────

    private function makeAgency(string $slug = 'ag'): Agency
    {
        return Agency::create([
            'name' => 'Agency '.strtoupper($slug),
            'slug' => $slug,
            'brand_name' => 'Agency '.strtoupper($slug),
            'status' => 'active',
            'billing_type' => 'monthly',
        ]);
    }

    private function makeRule(): PlatformFeeRule
    {
        return PlatformFeeRule::create([
            'plan_id' => null,
            'billing_type' => null,
            'fee_pct' => '0.2000',
            'fee_type' => 'platform_share',
            'valid_from' => now()->subDay(),
        ]);
    }

    private function makeRecord(Agency $agency, PlatformFeeRule $rule, array $overrides = []): CommissionRecord
    {
        return CommissionRecord::create(array_merge([
            'agency_id' => $agency->id,
            'platform_fee_rule_id' => $rule->id,
            'gross_amount_cents' => 10000,
            'fee_pct' => '0.2000',
            'fee_amount_cents' => 2000,
            'net_to_agency_cents' => 8000,
            'currency' => 'eur',
            'status' => CommissionRecord::STATUS_SETTLED,
            'settled_at' => now(),
        ], $overrides));
    }

    private function makeWidget(): AgencyStatsWidget
    {
        return app(AgencyStatsWidget::class);
    }

    // ── Tests ─────────────────────────────────────────────────────────────────

    public function test_returns_zeros_when_agency_has_no_commissions(): void
    {
        $agency = $this->makeAgency();
        $widget = $this->makeWidget();

        $result = $widget->monthlyRevenue($agency->id);

        $this->assertSame(0, $result['net']);
        $this->assertSame(0, $result['gross']);
        $this->assertSame(0, $result['count']);
    }

    public function test_only_settled_records_are_summed(): void
    {
        $agency = $this->makeAgency();
        $rule = $this->makeRule();

        // settled — should be counted
        $this->makeRecord($agency, $rule, ['status' => CommissionRecord::STATUS_SETTLED, 'net_to_agency_cents' => 8000]);

        // non-settled — must not appear in the stat
        foreach ([CommissionRecord::STATUS_PENDING, CommissionRecord::STATUS_FAILED, CommissionRecord::STATUS_DISPUTED] as $status) {
            $this->makeRecord($agency, $rule, ['status' => $status, 'settled_at' => now()]);
        }

        $result = $this->makeWidget()->monthlyRevenue($agency->id);

        $this->assertSame(1, $result['count']);
        $this->assertSame(8000, $result['net']);
    }

    public function test_only_records_in_current_month_are_summed(): void
    {
        $agency = $this->makeAgency();
        $rule = $this->makeRule();

        // current month
        $this->makeRecord($agency, $rule, ['settled_at' => now(), 'net_to_agency_cents' => 8000]);

        // previous month — must be excluded
        $this->makeRecord($agency, $rule, ['settled_at' => now()->subMonthNoOverflow(), 'net_to_agency_cents' => 5000]);

        $result = $this->makeWidget()->monthlyRevenue($agency->id);

        $this->assertSame(1, $result['count']);
        $this->assertSame(8000, $result['net']);
    }

    public function test_records_from_other_agencies_are_excluded(): void
    {
        $rule = $this->makeRule();
        $agencyA = $this->makeAgency('a');
        $agencyB = $this->makeAgency('b');

        $this->makeRecord($agencyA, $rule, ['net_to_agency_cents' => 9000]);
        $this->makeRecord($agencyB, $rule, ['net_to_agency_cents' => 6000]);

        $resultA = $this->makeWidget()->monthlyRevenue($agencyA->id);
        $resultB = $this->makeWidget()->monthlyRevenue($agencyB->id);

        $this->assertSame(9000, $resultA['net']);
        $this->assertSame(6000, $resultB['net']);
    }

    public function test_net_gross_and_count_are_all_correct(): void
    {
        $agency = $this->makeAgency();
        $rule = $this->makeRule();

        // two settled records this month
        $this->makeRecord($agency, $rule, ['gross_amount_cents' => 10000, 'net_to_agency_cents' => 8000, 'settled_at' => now()]);
        $this->makeRecord($agency, $rule, ['gross_amount_cents' => 5000,  'net_to_agency_cents' => 4000, 'settled_at' => now()]);

        $result = $this->makeWidget()->monthlyRevenue($agency->id);

        $this->assertSame(2, $result['count']);
        $this->assertSame(12000, $result['net']);
        $this->assertSame(15000, $result['gross']);
    }

    public function test_for_month_parameter_allows_querying_arbitrary_months(): void
    {
        $agency = $this->makeAgency();
        $rule = $this->makeRule();
        $lastMonth = now()->subMonthNoOverflow();

        // record settled last month
        $this->makeRecord($agency, $rule, ['settled_at' => $lastMonth, 'net_to_agency_cents' => 7000]);
        // record settled this month — must NOT appear when querying last month
        $this->makeRecord($agency, $rule, ['settled_at' => now(), 'net_to_agency_cents' => 9000]);

        $result = $this->makeWidget()->monthlyRevenue($agency->id, Carbon::parse($lastMonth));

        $this->assertSame(1, $result['count']);
        $this->assertSame(7000, $result['net']);
    }
}
