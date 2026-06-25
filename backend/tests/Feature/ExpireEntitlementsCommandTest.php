<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\Agency;
use App\Models\Central\AgencyEntitlement;
use App\Models\Central\AuditEvent;
use App\Models\Central\PluginCatalogItem;
use Illuminate\Support\Carbon;
use Tests\CentralTestCase;

/**
 * ExpireEntitlements command test suite.
 *
 * Tests:
 *  1.  active + ends_at in the past → becomes expired + audit logged
 *  2.  active + ends_at in the future → remains active, no audit
 *  3.  active + ends_at null → remains active, no audit
 *  4.  revoked entitlement → unchanged, no audit
 *  5.  already expired entitlement → unchanged (idempotent)
 *  6.  audit event logged exactly once per expiration
 *  7.  command idempotent: second run does not re-expire or re-audit
 *  8.  EVENT_ENTITLEMENT_EXPIRED constant and label exist in AuditEvent
 */
class ExpireEntitlementsCommandTest extends CentralTestCase
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

    private function makeCatalogItem(): PluginCatalogItem
    {
        self::$seq++;

        return PluginCatalogItem::create([
            'code' => 'test_pack_'.self::$seq,
            'type' => PluginCatalogItem::TYPE_BLOCK_PACK,
            'name' => 'Test Pack '.self::$seq,
            'status' => PluginCatalogItem::STATUS_ACTIVE,
        ]);
    }

    private function makeEntitlement(Agency $agency, PluginCatalogItem $item, string $status, ?Carbon $endsAt = null): AgencyEntitlement
    {
        return AgencyEntitlement::create([
            'agency_id' => $agency->id,
            'catalog_item_id' => $item->id,
            'source' => AgencyEntitlement::SOURCE_MANUAL,
            'status' => $status,
            'ends_at' => $endsAt,
        ]);
    }

    private function auditCount(AgencyEntitlement $entitlement): int
    {
        return AuditEvent::where('event', AuditEvent::EVENT_ENTITLEMENT_EXPIRED)
            ->where('subject_type', 'agency_entitlement')
            ->where('subject_id', (string) $entitlement->id)
            ->count();
    }

    private function runCommand(): void
    {
        $this->artisan('entitlements:expire')->assertExitCode(0);
    }

    // ── 1. Active + past ends_at → expired ────────────────────────────────────

    public function test_active_entitlement_with_past_ends_at_becomes_expired(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem();
        $entitlement = $this->makeEntitlement($agency, $item, AgencyEntitlement::STATUS_ACTIVE, now()->subHour());

        $this->runCommand();

        $entitlement->refresh();
        $this->assertEquals(AgencyEntitlement::STATUS_EXPIRED, $entitlement->status);
        $this->assertEquals(1, $this->auditCount($entitlement));
    }

    // ── 2. Active + future ends_at → stays active ─────────────────────────────

    public function test_active_entitlement_with_future_ends_at_stays_active(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem();
        $entitlement = $this->makeEntitlement($agency, $item, AgencyEntitlement::STATUS_ACTIVE, now()->addDay());

        $this->runCommand();

        $entitlement->refresh();
        $this->assertEquals(AgencyEntitlement::STATUS_ACTIVE, $entitlement->status);
        $this->assertEquals(0, $this->auditCount($entitlement));
    }

    // ── 3. Active + no ends_at → stays active ────────────────────────────────

    public function test_active_entitlement_without_ends_at_stays_active(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem();
        $entitlement = $this->makeEntitlement($agency, $item, AgencyEntitlement::STATUS_ACTIVE, null);

        $this->runCommand();

        $entitlement->refresh();
        $this->assertEquals(AgencyEntitlement::STATUS_ACTIVE, $entitlement->status);
        $this->assertEquals(0, $this->auditCount($entitlement));
    }

    // ── 4. Revoked → unchanged ────────────────────────────────────────────────

    public function test_revoked_entitlement_is_not_touched(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem();
        $entitlement = $this->makeEntitlement($agency, $item, AgencyEntitlement::STATUS_REVOKED, now()->subDay());

        $this->runCommand();

        $entitlement->refresh();
        $this->assertEquals(AgencyEntitlement::STATUS_REVOKED, $entitlement->status);
        $this->assertEquals(0, $this->auditCount($entitlement));
    }

    // ── 5. Already expired → unchanged ───────────────────────────────────────

    public function test_already_expired_entitlement_is_not_touched(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem();
        $entitlement = $this->makeEntitlement($agency, $item, AgencyEntitlement::STATUS_EXPIRED, now()->subDay());

        $this->runCommand();

        $entitlement->refresh();
        $this->assertEquals(AgencyEntitlement::STATUS_EXPIRED, $entitlement->status);
        $this->assertEquals(0, $this->auditCount($entitlement));
    }

    // ── 6. Audit logged exactly once per expiration ───────────────────────────

    public function test_audit_event_logged_exactly_once_per_expired_entitlement(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem();
        $entitlement = $this->makeEntitlement($agency, $item, AgencyEntitlement::STATUS_ACTIVE, now()->subMinutes(5));

        $this->runCommand();

        $this->assertEquals(1, $this->auditCount($entitlement));
    }

    // ── 7. Idempotent: second run does nothing ────────────────────────────────

    public function test_command_is_idempotent_on_second_run(): void
    {
        $agency = $this->makeAgency();
        $item = $this->makeCatalogItem();
        $entitlement = $this->makeEntitlement($agency, $item, AgencyEntitlement::STATUS_ACTIVE, now()->subHour());

        $this->runCommand();
        $this->runCommand();

        $entitlement->refresh();
        $this->assertEquals(AgencyEntitlement::STATUS_EXPIRED, $entitlement->status);
        $this->assertEquals(1, $this->auditCount($entitlement), 'Audit must be logged exactly once even on repeated runs');
    }

    // ── 8. AuditEvent constant and label ─────────────────────────────────────

    public function test_audit_event_expired_constant_and_label_exist(): void
    {
        $this->assertEquals('entitlement.expired', AuditEvent::EVENT_ENTITLEMENT_EXPIRED);
        $this->assertArrayHasKey(AuditEvent::EVENT_ENTITLEMENT_EXPIRED, AuditEvent::EVENT_LABELS);
    }
}
