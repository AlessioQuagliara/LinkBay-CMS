<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\Agency;
use App\Models\Central\AgencyMember;
use App\Models\Central\User;
use Tests\CentralTestCase;

/**
 * Covers the Agency public registration flow (POST /agency/register).
 *
 * Tests:
 *  1. Successful registration creates Agency + User + owner AgencyMember
 *  2. Agency status is 'pending' in test environment (app()->isLocal() = false)
 *  3. Duplicate email returns validation error
 *  4. Duplicate slug returns validation error
 *  5. TODO — welcome email (RegisterController does not currently send one)
 *  6. Missing/malformed slug returns validation error
 *  7. TODO — second-agency prevention (not currently enforced in controller)
 *  8. owner_user_id is set on Agency after successful registration
 */
class AgencyRegistrationFlowTest extends CentralTestCase
{
    // ── Helpers ───────────────────────────────────────────────────────────────

    private static int $seq = 0;

    /** Returns a fully-valid registration payload; overrides are merged on top. */
    private function validPayload(array $overrides = []): array
    {
        self::$seq++;

        return array_merge([
            'agency_name' => 'Test Agency '.self::$seq,
            'slug' => 'test-agency-'.self::$seq,
            'email' => 'owner'.self::$seq.'@example.com',
            'password' => 'password123',
            'password_confirmation' => 'password123',
        ], $overrides);
    }

    // ── Test 1 ────────────────────────────────────────────────────────────────

    public function test_store_creates_agency_user_and_owner_member(): void
    {
        $payload = $this->validPayload();

        // ── Submit registration form ──────────────────────────────────────────
        $response = $this->post(route('agency.register.store'), $payload);
        $response->assertRedirect();

        // ── Agency exists with correct name ───────────────────────────────────
        $agency = Agency::where('slug', $payload['slug'])->first();
        $this->assertNotNull($agency, 'Agency should be persisted');
        $this->assertEquals($payload['agency_name'], $agency->name);
        $this->assertEquals($payload['agency_name'], $agency->brand_name);

        // ── Central User exists ───────────────────────────────────────────────
        $user = User::where('email', $payload['email'])->first();
        $this->assertNotNull($user, 'User should be persisted');

        // ── AgencyMember with role=owner created ──────────────────────────────
        $member = AgencyMember::where('agency_id', $agency->id)
            ->where('user_id', $user->id)
            ->first();

        $this->assertNotNull($member, 'AgencyMember record should exist');
        $this->assertEquals(AgencyMember::ROLE_OWNER, $member->role);
        $this->assertEquals(AgencyMember::STATUS_ACTIVE, $member->status);
        $this->assertNotNull($member->accepted_at);
    }

    // ── Test 2 ────────────────────────────────────────────────────────────────

    public function test_agency_status_is_pending_in_non_local_environment(): void
    {
        // app()->isLocal() returns false when APP_ENV=testing → status set to 'pending'
        $payload = $this->validPayload();

        $this->post(route('agency.register.store'), $payload);

        $agency = Agency::where('slug', $payload['slug'])->first();

        $this->assertNotNull($agency);
        $this->assertEquals('pending', $agency->status);
    }

    // ── Test 3 ────────────────────────────────────────────────────────────────

    public function test_duplicate_email_fails_validation(): void
    {
        // ── Pre-existing user with the same email ─────────────────────────────
        User::create([
            'name' => 'Existing User',
            'email' => 'taken@example.com',
            'password' => bcrypt('pass'),
        ]);

        $payload = $this->validPayload(['email' => 'taken@example.com']);
        $response = $this->post(route('agency.register.store'), $payload);

        $response->assertRedirect();
        $response->assertSessionHasErrors(['email']);
    }

    // ── Test 4 ────────────────────────────────────────────────────────────────

    public function test_duplicate_slug_fails_validation(): void
    {
        // ── Pre-existing agency occupying the slug ────────────────────────────
        Agency::create([
            'name' => 'Existing Agency',
            'slug' => 'taken-slug',
            'brand_name' => 'Existing Agency',
            'status' => 'active',
            'billing_type' => 'monthly',
        ]);

        $payload = $this->validPayload(['slug' => 'taken-slug']);
        $response = $this->post(route('agency.register.store'), $payload);

        $response->assertRedirect();
        $response->assertSessionHasErrors(['slug']);
    }

    // ── Test 5 ────────────────────────────────────────────────────────────────

    // TODO — RegisterController does not currently dispatch a welcome email.
    // Implement when AgencyWelcomeMail (or equivalent) is added:
    //
    // public function test_owner_receives_welcome_email_after_registration(): void
    // {
    //     Mail::fake();
    //     $payload = $this->validPayload();
    //     $this->post(route('agency.register.store'), $payload);
    //     Mail::assertSent(\App\Mail\AgencyWelcomeMail::class,
    //         fn ($m) => $m->hasTo($payload['email'])
    //     );
    // }

    // ── Test 6 ────────────────────────────────────────────────────────────────

    // Note: RegisterController requires an explicit slug — there is no auto-generation
    // from agency_name. Tests below verify the slug validation rules enforced by the regex.

    public function test_missing_slug_fails_validation(): void
    {
        $payload = $this->validPayload();
        unset($payload['slug']);

        $response = $this->post(route('agency.register.store'), $payload);

        $response->assertRedirect();
        $response->assertSessionHasErrors(['slug']);
    }

    public function test_slug_starting_with_hyphen_fails_validation(): void
    {
        // Regex: /^[a-z0-9][a-z0-9-]*[a-z0-9]$/ — cannot start or end with '-'
        $payload = $this->validPayload(['slug' => '-bad-slug']);
        $response = $this->post(route('agency.register.store'), $payload);

        $response->assertRedirect();
        $response->assertSessionHasErrors(['slug']);
    }

    public function test_password_confirmation_mismatch_fails_validation(): void
    {
        $payload = $this->validPayload(['password_confirmation' => 'different_pass']);
        $response = $this->post(route('agency.register.store'), $payload);

        $response->assertRedirect();
        $response->assertSessionHasErrors(['password']);
    }

    // ── Test 7 ────────────────────────────────────────────────────────────────

    // TODO — RegisterController does not currently prevent a user from registering
    // a second agency (no existing-ownership check). Implement when that rule lands:
    //
    // public function test_owner_cannot_register_second_agency(): void
    // {
    //     $payload1 = $this->validPayload();
    //     $this->post(route('agency.register.store'), $payload1);
    //
    //     // Second attempt reusing the same owner email must be rejected
    //     $payload2 = $this->validPayload(['email' => $payload1['email']]);
    //     $response = $this->post(route('agency.register.store'), $payload2);
    //     $response->assertSessionHasErrors(['email']);
    // }

    // ── Test 8 ────────────────────────────────────────────────────────────────

    public function test_owner_user_id_is_stamped_on_agency_after_registration(): void
    {
        $payload = $this->validPayload();

        $this->post(route('agency.register.store'), $payload);

        $agency = Agency::where('slug', $payload['slug'])->first();
        $user = User::where('email', $payload['email'])->first();

        $this->assertNotNull($agency);
        $this->assertNotNull($user);
        $this->assertEquals($user->id, $agency->owner_user_id);
    }
}
