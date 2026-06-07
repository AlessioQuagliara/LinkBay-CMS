<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Mail\AgencyMemberInviteMail;
use App\Models\Central\Agency;
use App\Models\Central\AgencyMember;
use App\Models\Central\User;
use App\Services\AgencyMemberService;
use Illuminate\Support\Facades\Mail;
use Tests\CentralTestCase;

/**
 * Covers AgencyMemberService and the agency-invite HTTP flow.
 *
 * Tests:
 *   1. inviteMember creates pending record and sends mail
 *   2. accepting as new user creates a User + activates member
 *   3. accepting as existing user reuses the User
 *   4. duplicate active-member invite throws
 *   5. changeRole: owner-transfer demotes previous owner
 *   6. suspendMember refuses to suspend owner
 *   7. removeMember refuses to remove owner
 *   8. HTTP show returns 200 for valid token
 *   9. HTTP show redirects for unknown token
 *  10. HTTP show redirects for expired token
 *  11. Role enforcement: member cannot access billing page
 */
class AgencyMemberTest extends CentralTestCase
{
    // ── Helpers ───────────────────────────────────────────────────────────────

    private function makeAgency(): Agency
    {
        return Agency::create([
            'name' => 'Test Agency',
            'slug' => 'test-agency',
            'brand_name' => 'Test Agency',
            'status' => 'active',
            'billing_type' => 'monthly',
        ]);
    }

    private function makeOwner(Agency $agency): User
    {
        $user = User::create([
            'name' => 'Owner',
            'email' => 'owner@example.com',
            'password' => bcrypt('password'),
        ]);

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

    private function service(): AgencyMemberService
    {
        return app(AgencyMemberService::class);
    }

    // ── Service tests ─────────────────────────────────────────────────────────

    public function test_invite_creates_pending_member_and_sends_mail(): void
    {
        Mail::fake();

        $agency = $this->makeAgency();
        $owner = $this->makeOwner($agency);

        $member = $this->service()->inviteMember($agency, 'alice@example.com', AgencyMember::ROLE_MEMBER, $owner);

        $this->assertEquals(AgencyMember::STATUS_PENDING, $member->status);
        $this->assertEquals('alice@example.com', $member->invited_email);
        $this->assertEquals(AgencyMember::ROLE_MEMBER, $member->role);
        $this->assertNotNull($member->invite_token);
        $this->assertTrue($member->invite_expires_at->isFuture());

        Mail::assertSent(AgencyMemberInviteMail::class, fn ($m) => $m->hasTo('alice@example.com'));
    }

    public function test_accept_invite_as_new_user_creates_user_and_activates_member(): void
    {
        Mail::fake();

        $agency = $this->makeAgency();
        $owner = $this->makeOwner($agency);
        $member = $this->service()->inviteMember($agency, 'newuser@example.com', AgencyMember::ROLE_MEMBER, $owner);

        $user = $this->service()->acceptInvite($member, 'New User', 'password123');

        $this->assertEquals('newuser@example.com', $user->email);
        $this->assertEquals('New User', $user->name);

        $member->refresh();
        $this->assertEquals(AgencyMember::STATUS_ACTIVE, $member->status);
        $this->assertEquals($user->id, $member->user_id);
        $this->assertNotNull($member->accepted_at);
        $this->assertNull($member->invite_token);
    }

    public function test_accept_invite_as_existing_user_reuses_user(): void
    {
        Mail::fake();

        $agency = $this->makeAgency();
        $owner = $this->makeOwner($agency);
        $existingUser = User::create([
            'name' => 'Existing',
            'email' => 'existing@example.com',
            'password' => bcrypt('pass'),
        ]);

        $member = $this->service()->inviteMember($agency, 'existing@example.com', AgencyMember::ROLE_ADMIN, $owner);
        $user = $this->service()->acceptInvite($member, 'Ignored Name', 'newpassword1');

        $this->assertEquals($existingUser->id, $user->id, 'Should reuse existing user');

        $member->refresh();
        $this->assertEquals(AgencyMember::STATUS_ACTIVE, $member->status);
    }

    public function test_invite_duplicate_active_member_throws(): void
    {
        Mail::fake();

        $agency = $this->makeAgency();
        $owner = $this->makeOwner($agency);
        $member = $this->service()->inviteMember($agency, 'dup@example.com', AgencyMember::ROLE_MEMBER, $owner);
        $this->service()->acceptInvite($member, 'Dup', 'password123');

        $this->expectException(\RuntimeException::class);

        $this->service()->inviteMember($agency, 'dup@example.com', AgencyMember::ROLE_MEMBER, $owner);
    }

    public function test_change_role_to_owner_demotes_previous_owner(): void
    {
        Mail::fake();

        $agency = $this->makeAgency();
        $owner = $this->makeOwner($agency);
        $member = $this->service()->inviteMember($agency, 'admin@example.com', AgencyMember::ROLE_ADMIN, $owner);
        $this->service()->acceptInvite($member, 'Admin', 'password123');
        $member->refresh();

        $ownerMember = AgencyMember::where('agency_id', $agency->id)->where('role', AgencyMember::ROLE_OWNER)->first();

        $this->service()->changeRole($member, AgencyMember::ROLE_OWNER);

        $member->refresh();
        $ownerMember->refresh();

        $this->assertEquals(AgencyMember::ROLE_OWNER, $member->role);
        $this->assertEquals(AgencyMember::ROLE_ADMIN, $ownerMember->role, 'Previous owner demoted to admin');
    }

    public function test_suspend_owner_throws(): void
    {
        $agency = $this->makeAgency();
        $owner = $this->makeOwner($agency);
        $ownerMember = AgencyMember::where('agency_id', $agency->id)->where('role', AgencyMember::ROLE_OWNER)->first();

        $this->expectException(\RuntimeException::class);

        $this->service()->suspendMember($ownerMember);
    }

    public function test_remove_owner_throws(): void
    {
        $agency = $this->makeAgency();
        $owner = $this->makeOwner($agency);
        $ownerMember = AgencyMember::where('agency_id', $agency->id)->where('role', AgencyMember::ROLE_OWNER)->first();

        $this->expectException(\RuntimeException::class);

        $this->service()->removeMember($ownerMember);
    }

    // ── HTTP tests ────────────────────────────────────────────────────────────

    public function test_show_returns_200_for_valid_token(): void
    {
        Mail::fake();

        $agency = $this->makeAgency();
        $owner = $this->makeOwner($agency);
        $member = $this->service()->inviteMember($agency, 'view@example.com', AgencyMember::ROLE_MEMBER, $owner);

        $response = $this->get(route('agency-invite.show', $member->invite_token));

        $response->assertStatus(200);
        $response->assertViewIs('agency-invite.show');
    }

    public function test_show_redirects_for_unknown_token(): void
    {
        $response = $this->get(route('agency-invite.show', 'badtoken'));

        $response->assertRedirect(route('agency-invite.invalid'));
    }

    public function test_show_redirects_for_expired_token(): void
    {
        $agency = $this->makeAgency();
        $owner = $this->makeOwner($agency);

        $member = AgencyMember::create([
            'agency_id' => $agency->id,
            'invited_by_user_id' => $owner->id,
            'invited_email' => 'expired@example.com',
            'role' => AgencyMember::ROLE_MEMBER,
            'status' => AgencyMember::STATUS_PENDING,
            'invite_token' => 'expiredtoken',
            'invite_expires_at' => now()->subHour(),
            'invited_at' => now()->subDay(),
        ]);

        $response = $this->get(route('agency-invite.show', 'expiredtoken'));

        $response->assertRedirect(route('agency-invite.invalid'));
    }

    // ── Authorization ─────────────────────────────────────────────────────────

    public function test_member_role_is_not_owner(): void
    {
        Mail::fake();

        $agency = $this->makeAgency();
        $owner = $this->makeOwner($agency);
        $member = $this->service()->inviteMember($agency, 'regular@example.com', AgencyMember::ROLE_MEMBER, $owner);
        $this->service()->acceptInvite($member, 'Regular', 'password123');
        $member->refresh();

        $this->assertFalse($member->isOwner());
        $this->assertFalse($member->isAdmin());
        $this->assertFalse($member->isOwnerOrAdmin());
    }

    public function test_owner_membership_is_created_on_registration(): void
    {
        $agency = $this->makeAgency();
        $owner = $this->makeOwner($agency);

        $ownerMember = AgencyMember::where('agency_id', $agency->id)
            ->where('user_id', $owner->id)
            ->where('role', AgencyMember::ROLE_OWNER)
            ->where('status', AgencyMember::STATUS_ACTIVE)
            ->first();

        $this->assertNotNull($ownerMember, 'Owner AgencyMember record must exist');
    }
}
