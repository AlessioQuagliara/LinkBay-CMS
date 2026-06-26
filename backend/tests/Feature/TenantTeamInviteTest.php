<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Filament\Tenant\Pages\TeamPage;
use App\Models\Tenant\User;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Password;
use Illuminate\Validation\ValidationException;
use Tests\TenantTestCase;

/**
 * Covers TeamPage logic for Tenant panel team management.
 *
 * Uses TenantTestCase so only tenant DB migrations run (users table etc.),
 * avoiding conflicts with central migrations.
 *
 * Tests:
 *  1.  Tenant\User can be created with role constant
 *  2.  Tenant\User ROLE_OWNER constant is 'owner'
 *  3.  Tenant\User ROLE_EDITOR constant is 'editor'
 *  4.  Tenant\User ROLE_VIEWER constant is 'viewer'
 *  5.  roleLabelFor() maps roles to display strings
 *  6.  roleColorFor() maps owner to warning, editor to primary, else gray
 *  7.  getMembers() returns all users ordered by name
 *  8.  removeUser() deletes non-owner user
 *  9.  removeUser() refuses to delete owner
 * 10.  removeUser() refuses to delete the authenticated user themselves
 * 11.  inviteUser() creates user when email does not exist
 * 12.  inviteUser() does not duplicate existing user
 * 13.  inviteUser() validates email format
 * 14.  inviteUser() validates role is editor or viewer (not owner)
 */
class TenantTeamInviteTest extends TenantTestCase
{
    private function makeUser(string $role = User::ROLE_EDITOR): User
    {
        static $n = 0;
        $n++;

        return User::create([
            'name' => 'User '.$n,
            'email' => 'user'.$n.'@example.com',
            'password' => Hash::make('password'),
            'role' => $role,
        ]);
    }

    // ── Model constants ───────────────────────────────────────────────────────

    public function test_role_owner_constant(): void
    {
        $this->assertEquals('owner', User::ROLE_OWNER);
    }

    public function test_role_editor_constant(): void
    {
        $this->assertEquals('editor', User::ROLE_EDITOR);
    }

    public function test_role_viewer_constant(): void
    {
        $this->assertEquals('viewer', User::ROLE_VIEWER);
    }

    public function test_tenant_user_can_be_created_with_role(): void
    {
        $user = $this->makeUser(User::ROLE_OWNER);

        $this->assertDatabaseHas('users', ['email' => $user->email, 'role' => 'owner']);
    }

    // ── TeamPage helpers ──────────────────────────────────────────────────────

    public function test_role_label_for_maps_roles(): void
    {
        $page = new TeamPage;

        $this->assertEquals('Owner', $page->roleLabelFor('owner'));
        $this->assertEquals('Editor', $page->roleLabelFor('editor'));
        $this->assertEquals('Viewer', $page->roleLabelFor('viewer'));
        $this->assertEquals('Custom', $page->roleLabelFor('custom'));
    }

    public function test_role_color_for_maps_owner_to_warning(): void
    {
        $page = new TeamPage;

        $this->assertEquals('warning', $page->roleColorFor('owner'));
        $this->assertEquals('primary', $page->roleColorFor('editor'));
        $this->assertEquals('gray', $page->roleColorFor('viewer'));
    }

    public function test_get_members_returns_all_users_ordered_by_name(): void
    {
        User::create(['name' => 'Zara',  'email' => 'z@example.com', 'password' => 'x', 'role' => 'editor']);
        User::create(['name' => 'Alice', 'email' => 'a@example.com', 'password' => 'x', 'role' => 'owner']);

        $page = new TeamPage;
        $members = $page->getMembers();

        $this->assertCount(2, $members);
        $this->assertEquals('Alice', $members->first()->name);
    }

    // ── removeUser ────────────────────────────────────────────────────────────

    public function test_remove_user_deletes_non_owner(): void
    {
        $user = $this->makeUser(User::ROLE_EDITOR);
        $this->actingAs($this->makeUser(User::ROLE_OWNER));

        (new TeamPage)->removeUser($user->id);

        $this->assertDatabaseMissing('users', ['id' => $user->id]);
    }

    public function test_remove_user_refuses_to_delete_owner(): void
    {
        $owner = $this->makeUser(User::ROLE_OWNER);
        $this->actingAs($owner);

        (new TeamPage)->removeUser($owner->id);

        $this->assertDatabaseHas('users', ['id' => $owner->id]);
    }

    public function test_remove_user_refuses_to_delete_self(): void
    {
        $user = $this->makeUser(User::ROLE_EDITOR);
        $this->actingAs($user);

        (new TeamPage)->removeUser($user->id);

        $this->assertDatabaseHas('users', ['id' => $user->id]);
    }

    // ── inviteUser ────────────────────────────────────────────────────────────

    public function test_invite_user_creates_user_when_email_not_exists(): void
    {
        Password::shouldReceive('broker')
            ->with('tenant_users')
            ->andReturnSelf();
        Password::shouldReceive('sendResetLink')
            ->andReturn(Password::RESET_LINK_SENT);

        $page = new TeamPage;
        $page->inviteData = ['email' => 'newbie@example.com', 'role' => 'editor'];

        $page->inviteUser();

        $this->assertDatabaseHas('users', ['email' => 'newbie@example.com', 'role' => 'editor']);
    }

    public function test_invite_user_does_not_duplicate_existing_user(): void
    {
        $existing = $this->makeUser(User::ROLE_EDITOR);

        Password::shouldReceive('broker')->with('tenant_users')->andReturnSelf();
        Password::shouldReceive('sendResetLink')->andReturn(Password::RESET_LINK_SENT);

        $page = new TeamPage;
        $page->inviteData = ['email' => $existing->email, 'role' => 'editor'];
        $page->inviteUser();

        $this->assertCount(1, User::where('email', $existing->email)->get());
    }

    public function test_invite_user_validates_email(): void
    {
        $page = new TeamPage;
        $page->inviteData = ['email' => 'not-an-email', 'role' => 'editor'];

        $this->expectException(ValidationException::class);

        $page->inviteUser();
    }

    public function test_invite_user_rejects_owner_role(): void
    {
        $page = new TeamPage;
        $page->inviteData = ['email' => 'hacker@example.com', 'role' => 'owner'];

        $this->expectException(ValidationException::class);

        $page->inviteUser();
    }
}
