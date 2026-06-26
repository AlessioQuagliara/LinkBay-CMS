<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Http\Controllers\Tenant\TenantImpersonateController;
use App\Models\Tenant\User;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Hash;
use Symfony\Component\HttpKernel\Exception\HttpException;
use Tests\TenantTestCase;

/**
 * Covers TenantImpersonateController logic for agency-to-tenant impersonation.
 *
 * Uses TenantTestCase so the tenant users table is available for login/user-creation
 * assertions without pulling in central migrations.
 *
 * Tests:
 *  1.  generateToken() stores payload in cache under 'impersonate:{token}'
 *  2.  generateToken() returns a UUID-format token string
 *  3.  generateToken() stores email in payload
 *  4.  generateToken() stores tenant_id in payload
 *  5.  handle() aborts 403 for invalid (non-existent) token
 *  6.  handle() aborts 403 when token already consumed
 *  7.  handle() consumes (removes) the token after use
 *  8.  handle() logs in existing Tenant\User via tenant_web guard
 *  9.  handle() creates Tenant\User when email not found
 * 10.  handle() assigns ROLE_OWNER to newly created user
 * 11.  handle() redirects to /admin on success
 */
class AgencyClientImpersonationTest extends TenantTestCase
{
    private function makeUser(string $email = 'agent@agency.com'): User
    {
        return User::create([
            'name' => 'Agent',
            'email' => $email,
            'password' => Hash::make('secret'),
            'role' => User::ROLE_OWNER,
        ]);
    }

    private function putToken(string $email = 'agent@agency.com', string $tenantId = 'store-1'): string
    {
        $token = 'test-token-'.uniqid();
        Cache::put('impersonate:'.$token, [
            'email' => $email,
            'tenant_id' => $tenantId,
        ], now()->addMinutes(5));

        return $token;
    }

    // ── generateToken ─────────────────────────────────────────────────────────

    public function test_generate_token_stores_payload_in_cache(): void
    {
        $token = TenantImpersonateController::generateToken('owner@agency.com', 'store-abc');

        $this->assertNotNull(Cache::get('impersonate:'.$token));
    }

    public function test_generate_token_returns_uuid_string(): void
    {
        $token = TenantImpersonateController::generateToken('owner@agency.com', 'store-abc');

        $this->assertMatchesRegularExpression(
            '/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/',
            $token
        );
    }

    public function test_generate_token_stores_email_in_payload(): void
    {
        $token = TenantImpersonateController::generateToken('owner@agency.com', 'store-abc');

        $payload = Cache::get('impersonate:'.$token);
        $this->assertEquals('owner@agency.com', $payload['email']);
    }

    public function test_generate_token_stores_tenant_id_in_payload(): void
    {
        $token = TenantImpersonateController::generateToken('owner@agency.com', 'store-abc');

        $payload = Cache::get('impersonate:'.$token);
        $this->assertEquals('store-abc', $payload['tenant_id']);
    }

    // ── handle() – invalid tokens ─────────────────────────────────────────────

    public function test_handle_aborts_403_for_invalid_token(): void
    {
        $this->expectException(HttpException::class);

        (new TenantImpersonateController)->handle('this-token-does-not-exist');
    }

    public function test_handle_aborts_403_when_token_already_consumed(): void
    {
        $token = $this->putToken();

        // First use consumes it
        $this->makeUser('agent@agency.com');
        (new TenantImpersonateController)->handle($token);

        // Second use must fail
        $this->expectException(HttpException::class);
        (new TenantImpersonateController)->handle($token);
    }

    public function test_handle_consumes_token_on_success(): void
    {
        $this->makeUser('agent@agency.com');
        $token = $this->putToken();

        (new TenantImpersonateController)->handle($token);

        $this->assertNull(Cache::get('impersonate:'.$token));
    }

    // ── handle() – happy path ─────────────────────────────────────────────────

    public function test_handle_logs_in_existing_user(): void
    {
        $user = $this->makeUser('agent@agency.com');
        $token = $this->putToken('agent@agency.com');

        (new TenantImpersonateController)->handle($token);

        $this->assertTrue(Auth::guard('tenant_web')->check());
        $this->assertEquals($user->id, Auth::guard('tenant_web')->id());
    }

    public function test_handle_creates_user_when_email_not_found(): void
    {
        $token = $this->putToken('newagent@agency.com');

        (new TenantImpersonateController)->handle($token);

        $this->assertDatabaseHas('users', ['email' => 'newagent@agency.com']);
    }

    public function test_handle_assigns_owner_role_to_created_user(): void
    {
        $token = $this->putToken('newagent@agency.com');

        (new TenantImpersonateController)->handle($token);

        $this->assertDatabaseHas('users', [
            'email' => 'newagent@agency.com',
            'role' => User::ROLE_OWNER,
        ]);
    }

    public function test_handle_redirects_to_admin(): void
    {
        $this->makeUser('agent@agency.com');
        $token = $this->putToken('agent@agency.com');

        $response = (new TenantImpersonateController)->handle($token);

        $this->assertStringEndsWith('/admin', $response->getTargetUrl());
    }
}
