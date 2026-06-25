<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\Agency;
use App\Models\Central\AgencyEntitlement;
use App\Models\Central\AgencyHealthAlert;
use App\Models\Central\PluginCatalogItem;
use App\Models\Central\UsageEvent;
use App\Models\Central\User;
use App\Services\AgencyAlertService;
use Filament\Panel;
use Illuminate\Support\Facades\DB;
use Tests\CentralTestCase;

/**
 * Fase 6A — Early Warnings & Alerting test suite.
 *
 * Tests:
 *  1.  low_activity rule fires when activityLevel Low + trend Declining
 *  2.  premium_not_used rule fires for mature entitlement + zero premium usage
 *  3.  premium_not_used NOT triggered when entitlement is immature
 *  4.  design_drop rule fires when trend Declining + design not High + enough events
 *  5.  marketing_pack_inactive rule fires when marketing pack active + Low marketing usage
 *  6.  no duplicate alert created if same type+agency already open
 *  7.  evaluateAndStoreAlerts returns correct counts per type
 *  8.  agency with no problems produces no alerts
 *  9.  artisan command exits with SUCCESS
 * 10.  alert resolve() sets resolved_at to now
 * 11.  isOpen() reflects resolved_at state correctly
 * 12.  only super admin can access the admin panel (resource guarded by panel auth)
 */
class AgencyAlertsTest extends CentralTestCase
{
    private static int $seq = 0;

    // ── Helpers ───────────────────────────────────────────────────────────────

    private function makeAgency(): Agency
    {
        self::$seq++;

        return Agency::create([
            'name' => 'Alerts Agency '.self::$seq,
            'slug' => 'alerts-agency-'.self::$seq,
            'brand_name' => 'Alerts Agency '.self::$seq,
            'status' => 'active',
            'billing_type' => 'monthly',
        ]);
    }

    private function track(
        Agency $agency,
        string $eventType,
        int $count = 1,
        ?\DateTime $at = null,
    ): void {
        for ($i = 0; $i < $count; $i++) {
            UsageEvent::create([
                'agency_id' => $agency->id,
                'event_type' => $eventType,
                'event_group' => UsageEvent::GROUP_PANEL,
                'occurred_at' => $at ?? now(),
            ]);
        }
    }

    /**
     * Grant a premium entitlement, optionally back-dating created_at to simulate maturity.
     */
    private function grantEntitlement(
        Agency $agency,
        string $code = 'block_pack_marketing',
        string $type = PluginCatalogItem::TYPE_BLOCK_PACK,
        int $daysOld = 0,
    ): AgencyEntitlement {
        $item = PluginCatalogItem::firstOrCreate(
            ['code' => $code],
            [
                'type' => $type,
                'name' => ucwords(str_replace('_', ' ', $code)),
                'status' => PluginCatalogItem::STATUS_ACTIVE,
            ],
        );

        $entitlement = AgencyEntitlement::create([
            'agency_id' => $agency->id,
            'catalog_item_id' => $item->id,
            'source' => AgencyEntitlement::SOURCE_MANUAL,
            'status' => AgencyEntitlement::STATUS_ACTIVE,
        ]);

        if ($daysOld > 0) {
            DB::connection('central')
                ->table('agency_entitlements')
                ->where('id', $entitlement->id)
                ->update(['created_at' => now()->subDays($daysOld)]);
        }

        return $entitlement;
    }

    private function makeSuperAdmin(): User
    {
        self::$seq++;

        return User::create([
            'name' => 'Super Admin',
            'email' => 'superadmin'.self::$seq.'@example.com',
            'password' => bcrypt('password'),
            'is_super_admin' => true,
        ]);
    }

    private function makeRegularUser(): User
    {
        self::$seq++;

        return User::create([
            'name' => 'Regular',
            'email' => 'regular'.self::$seq.'@example.com',
            'password' => bcrypt('password'),
            'is_super_admin' => false,
        ]);
    }

    private function makePanelStub(string $id): Panel
    {
        $panel = $this->createMock(Panel::class);
        $panel->method('getId')->willReturn($id);

        return $panel;
    }

    private function svc(): AgencyAlertService
    {
        return app(AgencyAlertService::class);
    }

    // ── 1. Rule 1 — low_activity ──────────────────────────────────────────────

    public function test_low_activity_alert_created_when_activity_low_and_trend_declining(): void
    {
        $agency = $this->makeAgency();

        // Previous window (31–60 days ago): 10 events → above min_events threshold
        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 10, now()->subDays(45));

        // Current window: 3 events → activityLevel Low (< 10); trend = (3-10)/10 = -70% → Declining
        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 3);

        $created = $this->svc()->evaluateAndStoreAlerts(30);

        $this->assertArrayHasKey(AgencyHealthAlert::TYPE_LOW_ACTIVITY, $created);
        $this->assertSame(1, $created[AgencyHealthAlert::TYPE_LOW_ACTIVITY]);

        $alert = AgencyHealthAlert::where('agency_id', $agency->id)
            ->where('type', AgencyHealthAlert::TYPE_LOW_ACTIVITY)
            ->first();

        $this->assertNotNull($alert);
        $this->assertNull($alert->resolved_at);
        $this->assertSame('medium', $alert->severity);
    }

    // ── 2. Rule 2 — premium_not_used (mature entitlement) ────────────────────

    public function test_premium_not_used_alert_created_for_mature_entitlement_with_zero_usage(): void
    {
        $agency = $this->makeAgency();

        // Entitlement granted 40 days ago (> default min_days_since_premium = 30)
        $this->grantEntitlement($agency, 'block_pack_marketing', PluginCatalogItem::TYPE_BLOCK_PACK, 40);

        // No premium renders in the window → PremiumAdoptionLevel::None
        $created = $this->svc()->evaluateAndStoreAlerts(30);

        $this->assertArrayHasKey(AgencyHealthAlert::TYPE_PREMIUM_NOT_USED, $created);

        $alert = AgencyHealthAlert::where('agency_id', $agency->id)
            ->where('type', AgencyHealthAlert::TYPE_PREMIUM_NOT_USED)
            ->first();

        $this->assertNotNull($alert);
        $this->assertNull($alert->resolved_at);
    }

    // ── 3. Rule 2 — premium_not_used skipped for immature entitlement ─────────

    public function test_premium_not_used_not_triggered_for_immature_entitlement(): void
    {
        $agency = $this->makeAgency();

        // Entitlement granted today (0 days old), far below min_days_since_premium = 30
        $this->grantEntitlement($agency, 'block_pack_marketing', PluginCatalogItem::TYPE_BLOCK_PACK, 0);

        $created = $this->svc()->evaluateAndStoreAlerts(30);

        $this->assertArrayNotHasKey(AgencyHealthAlert::TYPE_PREMIUM_NOT_USED, $created);

        $count = AgencyHealthAlert::where('agency_id', $agency->id)
            ->where('type', AgencyHealthAlert::TYPE_PREMIUM_NOT_USED)
            ->count();
        $this->assertSame(0, $count);
    }

    // ── 4. Rule 3 — design_drop ───────────────────────────────────────────────

    public function test_design_drop_alert_created_when_trend_declining_and_design_not_high(): void
    {
        $agency = $this->makeAgency();

        // Previous window: 15 events → previous total = 15
        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 15, now()->subDays(45));

        // Current window: 10 events, 4 are design events → designUsageLevel Medium
        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 4); // design events
        $this->track($agency, UsageEvent::EVENT_BILLING_PORTAL_OPENED, 6); // non-design

        // totalEvents = 10, trend pct = (10-15)/15 * 100 ≈ -33% → Declining
        // designUsageLevel: 4 layout.saved → medium (>= 3 but < 10) → != High
        // totalEvents = 10 >= min_events_for_design_alert = 5

        $created = $this->svc()->evaluateAndStoreAlerts(30);

        $this->assertArrayHasKey(AgencyHealthAlert::TYPE_DESIGN_DROP, $created);

        $alert = AgencyHealthAlert::where('agency_id', $agency->id)
            ->where('type', AgencyHealthAlert::TYPE_DESIGN_DROP)
            ->first();

        $this->assertNotNull($alert);
    }

    // ── 5. Rule 4 — marketing_pack_inactive ───────────────────────────────────

    public function test_marketing_pack_inactive_alert_created_when_pack_active_and_usage_low(): void
    {
        $agency = $this->makeAgency();

        $this->grantEntitlement($agency, 'block_pack_marketing', PluginCatalogItem::TYPE_BLOCK_PACK);

        // Only 2 premium_block.rendered events → marketingUsageLevel Low (< 5)
        $this->track($agency, UsageEvent::EVENT_PREMIUM_BLOCK_RENDERED, 2);

        $created = $this->svc()->evaluateAndStoreAlerts(30);

        $this->assertArrayHasKey(AgencyHealthAlert::TYPE_MARKETING_PACK_INACTIVE, $created);

        $alert = AgencyHealthAlert::where('agency_id', $agency->id)
            ->where('type', AgencyHealthAlert::TYPE_MARKETING_PACK_INACTIVE)
            ->first();

        $this->assertNotNull($alert);
        $this->assertSame('low', $alert->severity);
    }

    // ── 6. No duplicate alerts ────────────────────────────────────────────────

    public function test_no_duplicate_alert_created_when_same_type_already_open(): void
    {
        $agency = $this->makeAgency();

        // Pre-existing open alert
        AgencyHealthAlert::create([
            'agency_id' => $agency->id,
            'type' => AgencyHealthAlert::TYPE_LOW_ACTIVITY,
            'severity' => AgencyHealthAlert::SEVERITY_MEDIUM,
            'detected_at' => now()->subDays(2),
        ]);

        // Setup conditions that would trigger low_activity again
        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 10, now()->subDays(45));
        $this->track($agency, UsageEvent::EVENT_LAYOUT_SAVED, 3);

        $this->svc()->evaluateAndStoreAlerts(30);

        $count = AgencyHealthAlert::where('agency_id', $agency->id)
            ->where('type', AgencyHealthAlert::TYPE_LOW_ACTIVITY)
            ->whereNull('resolved_at')
            ->count();

        $this->assertSame(1, $count);
    }

    // ── 7. Returns correct counts ─────────────────────────────────────────────

    public function test_evaluate_returns_correct_counts_per_type(): void
    {
        $agencyA = $this->makeAgency();
        $agencyB = $this->makeAgency();

        // agencyA → triggers low_activity
        $this->track($agencyA, UsageEvent::EVENT_LAYOUT_SAVED, 10, now()->subDays(45));
        $this->track($agencyA, UsageEvent::EVENT_LAYOUT_SAVED, 3);

        // agencyB → triggers low_activity too
        $this->track($agencyB, UsageEvent::EVENT_LAYOUT_SAVED, 10, now()->subDays(45));
        $this->track($agencyB, UsageEvent::EVENT_LAYOUT_SAVED, 2);

        $created = $this->svc()->evaluateAndStoreAlerts(30);

        $this->assertArrayHasKey(AgencyHealthAlert::TYPE_LOW_ACTIVITY, $created);
        $this->assertSame(2, $created[AgencyHealthAlert::TYPE_LOW_ACTIVITY]);
    }

    // ── 8. No alerts for healthy agency ──────────────────────────────────────

    public function test_no_alerts_created_for_agency_with_no_problems(): void
    {
        $agency = $this->makeAgency();

        // Zero events, zero entitlements
        // activityLevel = Low, trend = Stable (both windows below min_events=5 with 0 events)
        // Rule 1: Low + Stable → doesn't fire (needs Declining)
        // Rule 2: no entitlements → doesn't fire
        // Rule 3: Stable trend → doesn't fire
        // Rule 4: no marketing pack → doesn't fire

        $created = $this->svc()->evaluateAndStoreAlerts(30);

        $this->assertEmpty($created);

        $count = AgencyHealthAlert::where('agency_id', $agency->id)->count();
        $this->assertSame(0, $count);
    }

    // ── 9. Artisan command exits SUCCESS ──────────────────────────────────────

    public function test_artisan_command_exits_with_success(): void
    {
        $this->artisan('agency:health-alerts', ['--days' => 30])
            ->assertExitCode(0);
    }

    // ── 10. resolve() sets resolved_at ────────────────────────────────────────

    public function test_resolve_sets_resolved_at_timestamp(): void
    {
        $agency = $this->makeAgency();

        $alert = AgencyHealthAlert::create([
            'agency_id' => $agency->id,
            'type' => AgencyHealthAlert::TYPE_LOW_ACTIVITY,
            'severity' => AgencyHealthAlert::SEVERITY_MEDIUM,
            'detected_at' => now(),
        ]);

        $this->assertNull($alert->resolved_at);
        $this->assertTrue($alert->isOpen());

        $alert->resolve();

        $this->assertNotNull($alert->resolved_at);
        $this->assertFalse($alert->isOpen());
    }

    // ── 11. isOpen() reflects state ───────────────────────────────────────────

    public function test_is_open_returns_false_after_resolved(): void
    {
        $agency = $this->makeAgency();

        $alert = AgencyHealthAlert::create([
            'agency_id' => $agency->id,
            'type' => AgencyHealthAlert::TYPE_MARKETING_PACK_INACTIVE,
            'severity' => AgencyHealthAlert::SEVERITY_LOW,
            'detected_at' => now(),
            'resolved_at' => now(),
        ]);

        $this->assertFalse($alert->isOpen());
    }

    // ── 12. Admin panel access — super admin only ─────────────────────────────

    public function test_admin_panel_only_accessible_to_super_admin(): void
    {
        $superAdmin = $this->makeSuperAdmin();
        $regular = $this->makeRegularUser();

        $adminPanel = $this->makePanelStub('admin');

        $this->assertTrue($superAdmin->canAccessPanel($adminPanel));
        $this->assertFalse($regular->canAccessPanel($adminPanel));
    }
}
