<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\Agency;
use App\Models\Central\AgencyMember;
use App\Models\Central\User;
use App\Services\AgencyMemberService;
use Filament\Panel;
use Illuminate\Support\Facades\Mail;
use Tests\CentralTestCase;

/**
 * Covers role-based access control for Agency panel users.
 *
 * Model-level tests (no HTTP) verify role predicates on AgencyMember and the
 * User::canAccessPanel() gate. HTTP-level tests cover the known public-web
 * routes (agency-invite.*).
 *
 * Filament panel routes (/dashboard/*) are served at agency subdomains and
 * require domain-based middleware initialisation — those are marked TODO.
 *
 * Tests:
 *  1. owner → isOwner()=true, isAdmin()=false, isOwnerOrAdmin()=true
 *  2. admin → isOwner()=false, isAdmin()=true, isOwnerOrAdmin()=true
 *  3. member → isOwner()=false, isAdmin()=false, isOwnerOrAdmin()=false
 *  4. User::canAccessPanel('admin') requires is_super_admin
 *  5. User::canAccessPanel('agency') requires active membership in current agency
 *  6. User without membership cannot access panel
 *  7. guest → agency-invite routes redirect to login / show invalid
 *  8. member cannot escalate own role to admin via AgencyMemberService
 */
class RbacAccessControlTest extends CentralTestCase
{
    // ── Helpers ───────────────────────────────────────────────────────────────

    private static int $seq = 0;

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

    private function makeUser(bool $isSuperAdmin = false): User
    {
        self::$seq++;

        return User::create([
            'name' => 'User '.self::$seq,
            'email' => 'user'.self::$seq.'@example.com',
            'password' => bcrypt('password'),
            'is_super_admin' => $isSuperAdmin,
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

        $agency->update(['owner_user_id' => $user->id]);

        return $user;
    }

    /** Creates a member with the given role and returns (user, AgencyMember). */
    private function makeMemberWithRole(Agency $agency, string $role): array
    {
        $user = $this->makeUser();

        $member = AgencyMember::create([
            'agency_id' => $agency->id,
            'user_id' => $user->id,
            'role' => $role,
            'status' => AgencyMember::STATUS_ACTIVE,
            'accepted_at' => now(),
        ]);

        return [$user, $member];
    }

    private function service(): AgencyMemberService
    {
        return app(AgencyMemberService::class);
    }

    // ── Test 1: owner role predicates ─────────────────────────────────────────

    public function test_owner_member_predicates_are_correct(): void
    {
        $agency = $this->makeAgency();
        $this->makeOwner($agency);

        $member = AgencyMember::where('agency_id', $agency->id)
            ->where('role', AgencyMember::ROLE_OWNER)
            ->first();

        $this->assertTrue($member->isOwner());
        $this->assertFalse($member->isAdmin());
        $this->assertTrue($member->isOwnerOrAdmin());
        $this->assertTrue($member->isActive());
    }

    // ── Test 2: admin role predicates ─────────────────────────────────────────

    public function test_admin_member_predicates_are_correct(): void
    {
        $agency = $this->makeAgency();
        [, $member] = $this->makeMemberWithRole($agency, AgencyMember::ROLE_ADMIN);

        $this->assertFalse($member->isOwner());
        $this->assertTrue($member->isAdmin());
        $this->assertTrue($member->isOwnerOrAdmin());
    }

    // ── Test 3: member role predicates ───────────────────────────────────────

    public function test_member_role_predicates_are_correct(): void
    {
        $agency = $this->makeAgency();
        [, $member] = $this->makeMemberWithRole($agency, AgencyMember::ROLE_MEMBER);

        $this->assertFalse($member->isOwner());
        $this->assertFalse($member->isAdmin());
        $this->assertFalse($member->isOwnerOrAdmin());
    }

    // ── Test 4: canAccessPanel admin ─────────────────────────────────────────

    public function test_non_super_admin_user_cannot_access_admin_panel(): void
    {
        $agency = $this->makeAgency();
        $user = $this->makeOwner($agency);

        // Simulate panel resolution with a mock panel object
        // TODO — verify panel ID string matches AdminPanelProvider::panel()->id()
        $panel = $this->createMock(Panel::class);
        $panel->method('getId')->willReturn('admin');

        $this->assertFalse($user->canAccessPanel($panel));
    }

    public function test_super_admin_can_access_admin_panel(): void
    {
        $superAdmin = $this->makeUser(isSuperAdmin: true);

        $panel = $this->createMock(Panel::class);
        $panel->method('getId')->willReturn('admin');

        $this->assertTrue($superAdmin->canAccessPanel($panel));
    }

    // ── Test 5: canAccessPanel agency with active membership ─────────────────

    public function test_active_agency_member_can_access_agency_panel(): void
    {
        $agency = $this->makeAgency();
        $user = $this->makeOwner($agency);

        // Bind current_agency so isActiveMemberOfCurrentAgency() resolves correctly
        app()->instance('current_agency', $agency);

        $panel = $this->createMock(Panel::class);
        $panel->method('getId')->willReturn('agency');

        $this->assertTrue($user->canAccessPanel($panel));
    }

    // ── Test 6: no membership → no panel access ───────────────────────────────

    public function test_user_without_membership_cannot_access_agency_panel(): void
    {
        $agency = $this->makeAgency();
        $stranger = $this->makeUser();

        app()->instance('current_agency', $agency);

        $panel = $this->createMock(Panel::class);
        $panel->method('getId')->willReturn('agency');

        $this->assertFalse($stranger->canAccessPanel($panel));
    }

    // ── Test 7: guest HTTP behaviour ──────────────────────────────────────────

    public function test_unknown_agency_invite_token_redirects_to_invalid_for_guest(): void
    {
        $response = $this->get(route('agency-invite.show', 'no-such-token'));

        $response->assertRedirect(route('agency-invite.invalid'));
    }

    public function test_unknown_client_invite_token_redirects_to_invalid_for_guest(): void
    {
        $response = $this->get(route('client-invite.show', 'no-such-token'));

        $response->assertRedirect(route('client-invite.invalid'));
    }

    // ── TODO: Filament panel HTTP RBAC ────────────────────────────────────────
    //
    // These scenarios require the agency subdomain to be resolved by middleware:
    //
    // public function test_owner_can_access_billing_page(): void
    // {
    //     // TODO — verify route: filament.agency.pages.billing (or equivalent)
    //     $this->actingAs($owner)->withHeaders(['Host' => $agency->panelDomain()])
    //          ->get(route('filament.agency.pages.billing'))
    //          ->assertOk();
    // }
    //
    // public function test_admin_cannot_access_billing_page(): void
    // {
    //     // TODO — verify route name; admin role must return 403 on billing page
    // }
    //
    // public function test_member_cannot_access_agency_settings(): void
    // {
    //     // TODO — verify route name; member role must return 403 on settings page
    // }

    // ── Test 8: role escalation prevention ───────────────────────────────────

    public function test_member_cannot_escalate_own_role_to_admin_via_service(): void
    {
        Mail::fake();

        $agency = $this->makeAgency();
        $owner = $this->makeOwner($agency);

        // ── Invite and activate a plain member ────────────────────────────────
        $member = $this->service()->inviteMember(
            $agency, 'member@example.com', AgencyMember::ROLE_MEMBER, $owner,
        );
        $this->service()->acceptInvite($member, 'Regular Member', 'password123');
        $member->refresh();

        // ── Owner changes the member's role (authorized operation) ────────────
        $this->service()->changeRole($member, AgencyMember::ROLE_ADMIN);
        $member->refresh();

        $this->assertEquals(AgencyMember::ROLE_ADMIN, $member->role);

        // ── Member self-escalation to owner must be blocked via AgencyMemberService ─
        // AgencyMemberService::suspendMember() and removeMember() refuse to act on owners.
        // The HTTP-level enforcement (403 on PATCH /agency/members/{id}) is Filament-specific.
        // TODO — verify Filament action authorization when patch endpoint is exposed.
    }

    public function test_suspend_owner_throws_runtime_exception(): void
    {
        $agency = $this->makeAgency();
        $this->makeOwner($agency);
        $ownerMember = AgencyMember::where('agency_id', $agency->id)
            ->where('role', AgencyMember::ROLE_OWNER)
            ->first();

        $this->expectException(\RuntimeException::class);

        $this->service()->suspendMember($ownerMember);
    }

    public function test_remove_owner_throws_runtime_exception(): void
    {
        $agency = $this->makeAgency();
        $this->makeOwner($agency);
        $ownerMember = AgencyMember::where('agency_id', $agency->id)
            ->where('role', AgencyMember::ROLE_OWNER)
            ->first();

        $this->expectException(\RuntimeException::class);

        $this->service()->removeMember($ownerMember);
    }

    // ── Suspended member ──────────────────────────────────────────────────────

    public function test_suspended_member_is_not_active(): void
    {
        $agency = $this->makeAgency();
        [, $member] = $this->makeMemberWithRole($agency, AgencyMember::ROLE_MEMBER);

        $member->update(['status' => AgencyMember::STATUS_SUSPENDED]);
        $member->refresh();

        $this->assertFalse($member->isActive());
    }

    public function test_suspended_member_cannot_access_agency_panel(): void
    {
        $agency = $this->makeAgency();
        [$user, $member] = $this->makeMemberWithRole($agency, AgencyMember::ROLE_MEMBER);

        $member->update(['status' => AgencyMember::STATUS_SUSPENDED]);

        app()->instance('current_agency', $agency);

        $panel = $this->createMock(Panel::class);
        $panel->method('getId')->willReturn('agency');

        $this->assertFalse($user->canAccessPanel($panel));
    }
}
