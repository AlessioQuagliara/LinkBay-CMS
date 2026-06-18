<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Filament\Agency\Pages\AuditLogPage;
use App\Models\Central\Agency;
use App\Models\Central\AgencyMember;
use App\Models\Central\AuditEvent;
use App\Models\Central\User;
use App\Services\AgencyMemberService;
use App\Services\AuditEventService;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Mail;
use Tests\CentralTestCase;

/**
 * Covers AuditEventService and the hooks wired into AgencyMemberService.
 *
 * Tests:
 *  1.  AuditEventService::log() persists a record correctly
 *  2.  Default agency_id resolution from container binding
 *  3.  Default user_id resolution from auth guard
 *  4.  append-only: model has no updated_at column
 *  5.  agency_member.invited logged by inviteMember()
 *  6.  agency_member.accepted logged by acceptInvite()
 *  7.  agency_member.role_changed logged by changeRole() with old/new values
 *  8.  agency_member.suspended logged with correct old/new status
 *  9.  agency_member.reactivated logged
 * 10.  agency_member.removed logged before deletion (record still stored)
 * 11.  No sensitive data (invite_token / password) in audit values
 * 12.  Agency scoping: agency A's events not returned for agency B
 * 13.  AuditLogPage access: owner can access, member cannot
 */
class AuditEventServiceTest extends CentralTestCase
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

    private function makeUser(?string $email = null): User
    {
        self::$seq++;

        return User::create([
            'name' => 'User '.self::$seq,
            'email' => $email ?? 'user-'.self::$seq.'@test.com',
            'password' => bcrypt('password'),
        ]);
    }

    private function makeOwner(Agency $agency): User
    {
        $user = $this->makeUser();
        AgencyMember::create([
            'agency_id' => $agency->id,
            'user_id' => $user->id,
            'role' => AgencyMember::ROLE_OWNER,
            'status' => AgencyMember::STATUS_ACTIVE,
            'accepted_at' => now(),
        ]);

        return $user;
    }

    private function makeMember(Agency $agency, string $role = AgencyMember::ROLE_MEMBER): User
    {
        $user = $this->makeUser();
        AgencyMember::create([
            'agency_id' => $agency->id,
            'user_id' => $user->id,
            'role' => $role,
            'status' => AgencyMember::STATUS_ACTIVE,
            'accepted_at' => now(),
        ]);

        return $user;
    }

    private function makePendingMember(Agency $agency, string $email, string $role = AgencyMember::ROLE_MEMBER): AgencyMember
    {
        return AgencyMember::create([
            'agency_id' => $agency->id,
            'role' => $role,
            'status' => AgencyMember::STATUS_PENDING,
            'invited_email' => $email,
            'invite_token' => 'tok-'.uniqid(),
            'invite_expires_at' => now()->addHours(72),
        ]);
    }

    private function agencyMemberRecord(Agency $agency, User $user): AgencyMember
    {
        return AgencyMember::where('agency_id', $agency->id)
            ->where('user_id', $user->id)
            ->firstOrFail();
    }

    private function service(): AuditEventService
    {
        return app(AuditEventService::class);
    }

    private function memberService(): AgencyMemberService
    {
        return app(AgencyMemberService::class);
    }

    // ── 1. Basic persistence ──────────────────────────────────────────────────

    public function test_log_persists_audit_event_with_correct_fields(): void
    {
        $agency = $this->makeAgency();
        $user = $this->makeUser();

        $event = $this->service()->log(
            event: 'store.created',
            agencyId: $agency->id,
            userId: $user->id,
            subjectType: 'store',
            subjectId: 'my-store',
            newValues: ['name' => 'My Store'],
            metadata: ['admin_email' => 'admin@example.com'],
            ipAddress: '127.0.0.1',
        );

        $this->assertDatabaseHas('audit_events', [
            'agency_id' => $agency->id,
            'user_id' => $user->id,
            'event' => 'store.created',
            'subject_type' => 'store',
            'subject_id' => 'my-store',
            'ip_address' => '127.0.0.1',
        ], connection: 'central');

        $this->assertEquals(['name' => 'My Store'], $event->new_values);
        $this->assertEquals(['admin_email' => 'admin@example.com'], $event->metadata);
        $this->assertNotNull($event->created_at);
    }

    // ── 2. Default agency_id from container ───────────────────────────────────

    public function test_agency_id_resolved_from_container_when_not_provided(): void
    {
        $agency = $this->makeAgency();
        app()->instance('current_agency', $agency);

        $this->service()->log(event: 'terms.accepted');

        $this->assertDatabaseHas('audit_events', [
            'agency_id' => $agency->id,
            'event' => 'terms.accepted',
        ], connection: 'central');
    }

    // ── 3. Default user_id from auth ──────────────────────────────────────────

    public function test_user_id_resolved_from_auth_when_not_provided(): void
    {
        $user = $this->makeUser();
        $this->actingAs($user);

        $this->service()->log(event: 'store.created', agencyId: null);

        $this->assertDatabaseHas('audit_events', [
            'user_id' => $user->id,
            'event' => 'store.created',
        ], connection: 'central');
    }

    // ── 4. Append-only (no updated_at) ────────────────────────────────────────

    public function test_audit_event_has_no_updated_at_column(): void
    {
        $this->assertNull(AuditEvent::UPDATED_AT, 'AuditEvent must be append-only (no updated_at)');
    }

    public function test_audit_event_record_cannot_be_mass_assigned_updated_at(): void
    {
        $agency = $this->makeAgency();
        $event = $this->service()->log(event: 'store.created', agencyId: $agency->id);

        // The audit_events table has no updated_at column; calling fresh() should not throw.
        $fresh = $event->fresh();
        $this->assertNull($fresh->updated_at ?? null);
    }

    // ── 5. agency_member.invited ──────────────────────────────────────────────

    public function test_invite_member_logs_agency_member_invited(): void
    {
        $agency = $this->makeAgency();
        $inviter = $this->makeOwner($agency);
        $email = 'newmember@example.com';

        // Suppress actual mail sending.
        Mail::fake();

        $this->memberService()->inviteMember($agency, $email, AgencyMember::ROLE_MEMBER, $inviter);

        $this->assertDatabaseHas('audit_events', [
            'agency_id' => $agency->id,
            'user_id' => $inviter->id,
            'event' => AuditEvent::EVENT_MEMBER_INVITED,
        ], connection: 'central');

        $audit = AuditEvent::where('event', AuditEvent::EVENT_MEMBER_INVITED)
            ->where('agency_id', $agency->id)
            ->firstOrFail();

        $this->assertEquals($email, $audit->new_values['email']);
        $this->assertEquals(AgencyMember::ROLE_MEMBER, $audit->new_values['role']);
    }

    // ── 6. agency_member.accepted ─────────────────────────────────────────────

    public function test_accept_invite_logs_agency_member_accepted(): void
    {
        $agency = $this->makeAgency();
        $pending = $this->makePendingMember($agency, 'pending@example.com');

        $this->memberService()->acceptInvite($pending, 'New User', 'password123');

        $this->assertDatabaseHas('audit_events', [
            'agency_id' => $agency->id,
            'event' => AuditEvent::EVENT_MEMBER_ACCEPTED,
            'subject_type' => 'agency_member',
        ], connection: 'central');
    }

    // ── 7. agency_member.role_changed with old/new values ────────────────────

    public function test_change_role_logs_with_old_and_new_role(): void
    {
        $agency = $this->makeAgency();
        $user = $this->makeMember($agency, AgencyMember::ROLE_MEMBER);
        $record = $this->agencyMemberRecord($agency, $user);

        $this->memberService()->changeRole($record, AgencyMember::ROLE_ADMIN);

        $audit = AuditEvent::where('event', AuditEvent::EVENT_MEMBER_ROLE_CHANGED)
            ->where('agency_id', $agency->id)
            ->firstOrFail();

        $this->assertEquals(AgencyMember::ROLE_MEMBER, $audit->old_values['role']);
        $this->assertEquals(AgencyMember::ROLE_ADMIN, $audit->new_values['role']);
    }

    // ── 8. agency_member.suspended ────────────────────────────────────────────

    public function test_suspend_member_logs_status_transition(): void
    {
        $agency = $this->makeAgency();
        $user = $this->makeMember($agency, AgencyMember::ROLE_MEMBER);
        $record = $this->agencyMemberRecord($agency, $user);

        $this->memberService()->suspendMember($record);

        $audit = AuditEvent::where('event', AuditEvent::EVENT_MEMBER_SUSPENDED)
            ->where('agency_id', $agency->id)
            ->firstOrFail();

        $this->assertEquals(AgencyMember::STATUS_ACTIVE, $audit->old_values['status']);
        $this->assertEquals(AgencyMember::STATUS_SUSPENDED, $audit->new_values['status']);
    }

    // ── 9. agency_member.reactivated ─────────────────────────────────────────

    public function test_reactivate_member_logs_event(): void
    {
        $agency = $this->makeAgency();
        $user = $this->makeUser();
        AgencyMember::create([
            'agency_id' => $agency->id,
            'user_id' => $user->id,
            'role' => AgencyMember::ROLE_MEMBER,
            'status' => AgencyMember::STATUS_SUSPENDED,
            'accepted_at' => now(),
        ]);
        $record = $this->agencyMemberRecord($agency, $user);

        $this->memberService()->reactivateMember($record);

        $this->assertDatabaseHas('audit_events', [
            'event' => AuditEvent::EVENT_MEMBER_REACTIVATED,
            'agency_id' => $agency->id,
        ], connection: 'central');
    }

    // ── 10. agency_member.removed persisted after deletion ───────────────────

    public function test_remove_member_logs_event_even_after_deletion(): void
    {
        $agency = $this->makeAgency();
        $user = $this->makeMember($agency);
        $record = $this->agencyMemberRecord($agency, $user);
        $memberId = $record->id;

        $this->memberService()->removeMember($record);

        // Member record is gone.
        $this->assertDatabaseMissing('agency_members', ['id' => $memberId], connection: 'central');

        // Audit event is persisted with the subject_id still matching.
        $audit = AuditEvent::where('event', AuditEvent::EVENT_MEMBER_REMOVED)
            ->where('agency_id', $agency->id)
            ->firstOrFail();

        $this->assertEquals((string) $memberId, $audit->subject_id);
        $this->assertNotNull($audit->old_values['email']);
        $this->assertNotNull($audit->old_values['role']);
    }

    // ── 11. No sensitive data in audit values ─────────────────────────────────

    public function test_invite_token_not_logged_in_audit_values(): void
    {
        $agency = $this->makeAgency();
        $inviter = $this->makeOwner($agency);

        Mail::fake();

        $this->memberService()->inviteMember($agency, 'target@example.com', AgencyMember::ROLE_MEMBER, $inviter);

        $audit = AuditEvent::where('event', AuditEvent::EVENT_MEMBER_INVITED)
            ->where('agency_id', $agency->id)
            ->firstOrFail();

        $allValues = array_merge(
            $audit->new_values ?? [],
            $audit->old_values ?? [],
            $audit->metadata ?? [],
        );

        $this->assertArrayNotHasKey('invite_token', $allValues, 'invite_token must never be logged');
        $this->assertArrayNotHasKey('password', $allValues, 'password must never be logged');
    }

    public function test_accepted_invite_does_not_log_password(): void
    {
        $agency = $this->makeAgency();
        $pending = $this->makePendingMember($agency, 'pending2@example.com');

        $this->memberService()->acceptInvite($pending, 'Test User', 'supersecret123');

        $audit = AuditEvent::where('event', AuditEvent::EVENT_MEMBER_ACCEPTED)
            ->where('agency_id', $agency->id)
            ->firstOrFail();

        $allValues = array_merge(
            $audit->new_values ?? [],
            $audit->old_values ?? [],
            $audit->metadata ?? [],
        );

        $this->assertArrayNotHasKey('password', $allValues, 'password must never be logged');
        $this->assertArrayNotHasKey('invite_token', $allValues);
    }

    // ── 12. Agency scoping ────────────────────────────────────────────────────

    public function test_events_are_scoped_to_their_agency(): void
    {
        $agencyA = $this->makeAgency();
        $agencyB = $this->makeAgency();

        $this->service()->log(event: 'store.created', agencyId: $agencyA->id);
        $this->service()->log(event: 'store.created', agencyId: $agencyB->id);

        $eventsA = AuditEvent::where('agency_id', $agencyA->id)->count();
        $eventsB = AuditEvent::where('agency_id', $agencyB->id)->count();

        $this->assertEquals(1, $eventsA);
        $this->assertEquals(1, $eventsB);
    }

    public function test_cross_agency_events_do_not_bleed(): void
    {
        $agencyA = $this->makeAgency();
        $agencyB = $this->makeAgency();

        $this->service()->log(event: 'terms.accepted', agencyId: $agencyA->id);

        $this->assertEquals(0, AuditEvent::where('agency_id', $agencyB->id)->count());
    }

    // ── 13. AuditLogPage access control ──────────────────────────────────────

    public function test_audit_log_page_accessible_to_owner(): void
    {
        $agency = $this->makeAgency();
        $owner = $this->makeOwner($agency);

        app()->instance('current_agency', $agency);
        $this->actingAs($owner);

        $this->assertTrue(AuditLogPage::canAccess());
    }

    public function test_audit_log_page_accessible_to_admin(): void
    {
        $agency = $this->makeAgency();
        $admin = $this->makeMember($agency, AgencyMember::ROLE_ADMIN);

        app()->instance('current_agency', $agency);
        $this->actingAs($admin);

        $this->assertTrue(AuditLogPage::canAccess());
    }

    public function test_audit_log_page_not_accessible_to_member(): void
    {
        $agency = $this->makeAgency();
        $member = $this->makeMember($agency, AgencyMember::ROLE_MEMBER);

        app()->instance('current_agency', $agency);
        $this->actingAs($member);

        $this->assertFalse(AuditLogPage::canAccess());
    }

    public function test_audit_log_page_not_accessible_when_unauthenticated(): void
    {
        $agency = $this->makeAgency();
        app()->instance('current_agency', $agency);

        $this->assertFalse(AuditLogPage::canAccess());
    }

    // ── 14. AuditLogPage filter helpers ──────────────────────────────────────

    public function test_events_method_returns_only_current_agency_events(): void
    {
        $agencyA = $this->makeAgency();
        $agencyB = $this->makeAgency();
        $owner = $this->makeOwner($agencyA);

        $this->service()->log(event: 'store.created', agencyId: $agencyA->id);
        $this->service()->log(event: 'store.created', agencyId: $agencyB->id);

        app()->instance('current_agency', $agencyA);
        $this->actingAs($owner);

        $page = app(AuditLogPage::class);
        $events = $page->events();

        $this->assertCount(1, $events);
        $this->assertEquals($agencyA->id, $events->first()->agency_id);
    }

    public function test_event_type_filter_narrows_results(): void
    {
        $agency = $this->makeAgency();
        $owner = $this->makeOwner($agency);

        $this->service()->log(event: 'store.created', agencyId: $agency->id);
        $this->service()->log(event: 'terms.accepted', agencyId: $agency->id);

        app()->instance('current_agency', $agency);
        $this->actingAs($owner);

        $page = app(AuditLogPage::class);
        $page->filterEvent = 'store.created';

        $events = $page->events();

        $this->assertCount(1, $events);
        $this->assertEquals('store.created', $events->first()->event);
    }

    public function test_date_range_filter_excludes_events_outside_range(): void
    {
        $agency = $this->makeAgency();
        $owner = $this->makeOwner($agency);

        // Old event (61 days ago)
        DB::connection('central')->table('audit_events')->insert([
            'agency_id' => $agency->id,
            'event' => 'store.created',
            'created_at' => now()->subDays(61)->toDateTimeString(),
        ]);
        // Recent event (5 days ago)
        DB::connection('central')->table('audit_events')->insert([
            'agency_id' => $agency->id,
            'event' => 'terms.accepted',
            'created_at' => now()->subDays(5)->toDateTimeString(),
        ]);

        app()->instance('current_agency', $agency);
        $this->actingAs($owner);

        $page = app(AuditLogPage::class);
        $page->filterDateFrom = now()->subDays(30)->toDateString();

        $events = $page->events();

        $this->assertCount(1, $events);
        $this->assertEquals('terms.accepted', $events->first()->event);
    }

    public function test_user_filter_shows_only_that_actors_events(): void
    {
        $agency = $this->makeAgency();
        $userA = $this->makeOwner($agency);
        $userB = $this->makeMember($agency, AgencyMember::ROLE_ADMIN);

        $this->service()->log(event: 'store.created', agencyId: $agency->id, userId: $userA->id);
        $this->service()->log(event: 'store.created', agencyId: $agency->id, userId: $userB->id);

        app()->instance('current_agency', $agency);
        $this->actingAs($userA);

        $page = app(AuditLogPage::class);
        $page->filterUser = (string) $userA->id;

        $events = $page->events();

        $this->assertCount(1, $events);
        $this->assertEquals($userA->id, $events->first()->user_id);
    }
}
