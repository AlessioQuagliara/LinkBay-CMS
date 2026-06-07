<?php

declare(strict_types=1);

namespace Tests\Feature\Auth;

use App\Models\Central\Agency;
use App\Models\Central\User;
use PHPUnit\Framework\Attributes\DataProvider;
use Tests\CentralTestCase;

/**
 * Covers POST /agency/register and GET /agency/register.
 *
 * Verifies:
 *  - Happy path creates Agency and User records on the central connection.
 *  - Duplicate slug is rejected (unique rule uses central connection).
 *  - Duplicate email is rejected (unique rule uses central connection).
 *  - Invalid slug format is rejected by the regex rule.
 *  - Short password is rejected.
 *  - Mismatched password_confirmation is rejected.
 *  - Required fields are enforced.
 */
class AgencyRegistrationTest extends CentralTestCase
{
    // ── GET /agency/register ──────────────────────────────────────────────────

    public function test_registration_form_is_accessible(): void
    {
        $response = $this->get('/agency/register');

        $response->assertOk();
    }

    // ── POST /agency/register – happy path ────────────────────────────────────

    public function test_registration_creates_agency_and_user(): void
    {
        $response = $this->post('/agency/register', [
            'agency_name' => 'Delta Studio',
            'slug' => 'delta-studio',
            'email' => 'owner@delta-studio.com',
            'password' => 'secret1234',
            'password_confirmation' => 'secret1234',
        ]);

        $response->assertRedirect();

        $this->assertDatabaseHas('agencies', [
            'slug' => 'delta-studio',
            'name' => 'Delta Studio',
        ], 'central');

        $this->assertDatabaseHas('users', [
            'email' => 'owner@delta-studio.com',
        ], 'central');
    }

    public function test_registration_links_owner_to_agency(): void
    {
        $this->post('/agency/register', [
            'agency_name' => 'Delta Studio',
            'slug' => 'delta-studio',
            'email' => 'owner@delta-studio.com',
            'password' => 'secret1234',
            'password_confirmation' => 'secret1234',
        ]);

        $agency = Agency::where('slug', 'delta-studio')->first();
        $user = User::where('email', 'owner@delta-studio.com')->first();

        $this->assertNotNull($agency);
        $this->assertNotNull($user);
        $this->assertSame($user->id, $agency->owner_user_id);
    }

    public function test_registration_sets_pending_status_in_non_local_environment(): void
    {
        $this->post('/agency/register', [
            'agency_name' => 'Delta Studio',
            'slug' => 'delta-studio',
            'email' => 'owner@delta-studio.com',
            'password' => 'secret1234',
            'password_confirmation' => 'secret1234',
        ]);

        // APP_ENV=testing (not local) → status must be 'pending'
        $agency = Agency::where('slug', 'delta-studio')->first();

        $this->assertSame('pending', $agency->status);
    }

    // ── POST /agency/register – duplicate slug ────────────────────────────────

    public function test_duplicate_slug_is_rejected(): void
    {
        Agency::create([
            'name' => 'Existing Agency',
            'slug' => 'delta-studio',
            'brand_name' => 'Existing',
            'status' => 'active',
            'billing_type' => 'monthly',
        ]);

        $response = $this->post('/agency/register', [
            'agency_name' => 'Another Agency',
            'slug' => 'delta-studio',
            'email' => 'other@example.com',
            'password' => 'secret1234',
            'password_confirmation' => 'secret1234',
        ]);

        $response->assertSessionHasErrors('slug');
    }

    // ── POST /agency/register – duplicate email ───────────────────────────────

    public function test_duplicate_email_is_rejected(): void
    {
        User::create([
            'name' => 'Existing User',
            'email' => 'owner@delta-studio.com',
            'password' => bcrypt('password'),
        ]);

        $response = $this->post('/agency/register', [
            'agency_name' => 'Delta Studio',
            'slug' => 'delta-studio',
            'email' => 'owner@delta-studio.com',
            'password' => 'secret1234',
            'password_confirmation' => 'secret1234',
        ]);

        $response->assertSessionHasErrors('email');
    }

    // ── POST /agency/register – slug format ───────────────────────────────────

    #[DataProvider('invalidSlugProvider')]
    public function test_invalid_slug_format_is_rejected(string $slug): void
    {
        $response = $this->post('/agency/register', [
            'agency_name' => 'Test Agency',
            'slug' => $slug,
            'email' => 'owner@example.com',
            'password' => 'secret1234',
            'password_confirmation' => 'secret1234',
        ]);

        $response->assertSessionHasErrors('slug');
    }

    /** @return array<string, array{string}> */
    public static function invalidSlugProvider(): array
    {
        return [
            'starts with hyphen' => ['-bad-slug'],
            'ends with hyphen' => ['bad-slug-'],
            'contains uppercase' => ['BadSlug'],
            'contains spaces' => ['bad slug'],
            'contains underscore' => ['bad_slug'],
            'too short (1 char)' => ['a'],
        ];
    }

    // ── POST /agency/register – password rules ────────────────────────────────

    public function test_password_too_short_is_rejected(): void
    {
        $response = $this->post('/agency/register', [
            'agency_name' => 'Delta Studio',
            'slug' => 'delta-studio',
            'email' => 'owner@example.com',
            'password' => 'short',
            'password_confirmation' => 'short',
        ]);

        $response->assertSessionHasErrors('password');
    }

    public function test_password_confirmation_mismatch_is_rejected(): void
    {
        $response = $this->post('/agency/register', [
            'agency_name' => 'Delta Studio',
            'slug' => 'delta-studio',
            'email' => 'owner@example.com',
            'password' => 'secret1234',
            'password_confirmation' => 'different5678',
        ]);

        $response->assertSessionHasErrors('password');
    }

    // ── POST /agency/register – required fields ───────────────────────────────

    public function test_required_fields_are_enforced(): void
    {
        $response = $this->post('/agency/register', []);

        $response->assertSessionHasErrors(['agency_name', 'slug', 'email', 'password']);
    }
}
