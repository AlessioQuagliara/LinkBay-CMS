<?php

declare(strict_types=1);

namespace Tests\Feature\Tenant;

use App\Models\Tenant\Customer;
use Tests\Concerns\InteractsWithTenantRoutes;
use Tests\TenantTestCase;

/**
 * Covers the customer-facing auth + profile flow end-to-end over real Sanctum
 * bearer tokens (register/login issue a token; protected routes are called
 * with it), not Sanctum::actingAs — this is the exact flow flagged as broken
 * in the storefront audit (token vs session mismatch), now token-based.
 */
class CustomerAuthApiTest extends TenantTestCase
{
    use InteractsWithTenantRoutes;

    protected function setUp(): void
    {
        parent::setUp();
        $this->bypassTenantDomainResolution();
    }

    private function authHeaders(string $token): array
    {
        return ['Authorization' => "Bearer {$token}"];
    }

    public function test_register_creates_customer_and_returns_bearer_token(): void
    {
        $response = $this->postJson('/api/account/register', [
            'name' => 'Mario Rossi',
            'email' => 'mario@example.com',
            'password' => 'password123',
            'password_confirmation' => 'password123',
        ]);

        $response->assertCreated();
        $this->assertNotEmpty($response->json('data.token'));
        $this->assertSame('Bearer', $response->json('data.token_type'));
        $this->assertDatabaseHas('customers', ['email' => 'mario@example.com']);
    }

    public function test_register_rejects_duplicate_email(): void
    {
        Customer::factory()->create(['email' => 'exists@example.com']);

        $response = $this->postJson('/api/account/register', [
            'name' => 'Someone Else',
            'email' => 'exists@example.com',
            'password' => 'password123',
            'password_confirmation' => 'password123',
        ]);

        $response->assertStatus(422);
    }

    public function test_register_requires_password_confirmation(): void
    {
        $response = $this->postJson('/api/account/register', [
            'name' => 'Mario Rossi',
            'email' => 'mario2@example.com',
            'password' => 'password123',
            'password_confirmation' => 'not-matching',
        ]);

        $response->assertStatus(422);
        $response->assertJsonValidationErrors(['password']);
    }

    public function test_login_returns_bearer_token_for_valid_credentials(): void
    {
        Customer::factory()->create(['email' => 'login@example.com']);

        $response = $this->postJson('/api/account/login', [
            'email' => 'login@example.com',
            'password' => 'password',
        ]);

        $response->assertOk();
        $this->assertNotEmpty($response->json('data.token'));
    }

    public function test_login_rejects_invalid_password(): void
    {
        Customer::factory()->create(['email' => 'login2@example.com']);

        $response = $this->postJson('/api/account/login', [
            'email' => 'login2@example.com',
            'password' => 'wrong-password',
        ]);

        $response->assertStatus(401);
    }

    public function test_login_rejects_inactive_customer(): void
    {
        Customer::factory()->create(['email' => 'inactive@example.com', 'status' => 'blocked']);

        $response = $this->postJson('/api/account/login', [
            'email' => 'inactive@example.com',
            'password' => 'password',
        ]);

        $response->assertStatus(401);
    }

    public function test_authenticated_customer_can_fetch_profile_with_bearer_token(): void
    {
        Customer::factory()->create(['email' => 'profile@example.com', 'name' => 'Profile Customer']);

        $token = $this->postJson('/api/account/login', [
            'email' => 'profile@example.com',
            'password' => 'password',
        ])->json('data.token');

        $response = $this->getJson('/api/account/profile', $this->authHeaders($token));

        $response->assertOk();
        $response->assertJsonPath('data.name', 'Profile Customer');
    }

    public function test_profile_endpoint_rejects_request_without_token(): void
    {
        $response = $this->getJson('/api/account/profile');

        $response->assertUnauthorized();
    }

    public function test_profile_endpoint_rejects_invalid_token(): void
    {
        $response = $this->getJson('/api/account/profile', $this->authHeaders('this-is-not-a-real-token'));

        $response->assertUnauthorized();
    }

    public function test_customer_can_update_own_profile(): void
    {
        Customer::factory()->create(['email' => 'update@example.com', 'name' => 'Old Name']);

        $token = $this->postJson('/api/account/login', [
            'email' => 'update@example.com',
            'password' => 'password',
        ])->json('data.token');

        $response = $this->putJson('/api/account/profile', [
            'name' => 'New Name',
        ], $this->authHeaders($token));

        $response->assertOk();
        $this->assertDatabaseHas('customers', ['email' => 'update@example.com', 'name' => 'New Name']);
    }

    public function test_logout_revokes_the_token(): void
    {
        Customer::factory()->create(['email' => 'logout@example.com']);

        $token = $this->postJson('/api/account/login', [
            'email' => 'logout@example.com',
            'password' => 'password',
        ])->json('data.token');

        $this->postJson('/api/account/logout', [], $this->authHeaders($token))->assertOk();

        // Sanctum's guard memoizes the resolved user for its instance lifetime, and
        // AuthManager caches guard instances across calls within one test method
        // (unlike separate real HTTP requests, which each boot a fresh app). Without
        // this, the next call below would reuse the guard resolved during logout
        // instead of re-checking the now-deleted token.
        $this->app['auth']->forgetGuards();

        $response = $this->getJson('/api/account/profile', $this->authHeaders($token));
        $response->assertUnauthorized();
    }
}
