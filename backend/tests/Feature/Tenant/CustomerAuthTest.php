<?php

declare(strict_types=1);

namespace Tests\Feature\Tenant;

use App\Http\Middleware\AuthenticateCustomer;
use App\Http\Middleware\RedirectIfCustomerAuthenticated;
use App\Models\Tenant\Customer;
use App\Services\Tenant\CustomerAuthService;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\ValidationException;
use Laravel\Sanctum\PersonalAccessToken;
use Laravel\Sanctum\Sanctum;
use Tests\TenantTestCase;

/**
 * Customer auth is token-based (Sanctum personal access tokens on the
 * 'customer' guard), not session-based — see config/auth.php. These tests
 * exercise the service layer directly plus the guard/middleware wiring,
 * since HTTP-level tenant-domain routing (InitializeTenancyByDomain) has
 * no test harness in this codebase yet.
 */
class CustomerAuthTest extends TenantTestCase
{
    private CustomerAuthService $authService;

    protected function setUp(): void
    {
        parent::setUp();
        $this->authService = new CustomerAuthService;
    }

    private function makeCustomer(string $email = 'buyer@example.com', string $password = 'secret1234'): Customer
    {
        $customer = new Customer([
            'name' => 'Test Buyer',
            'email' => $email,
            'password' => Hash::make($password),
            'status' => 'active',
        ]);
        $customer->save();

        return $customer;
    }

    // ── register() ────────────────────────────────────────────────────────────

    public function test_register_creates_customer_and_issues_a_token(): void
    {
        $token = $this->authService->register([
            'name' => 'New Buyer',
            'email' => 'new@example.com',
            'password' => 'secret1234',
        ]);

        $this->assertDatabaseHas('customers', ['email' => 'new@example.com']);
        $this->assertNotEmpty($token->plainTextToken);

        $accessToken = PersonalAccessToken::findToken($token->plainTextToken);
        $this->assertNotNull($accessToken);
        $this->assertTrue($accessToken->tokenable->is(Customer::where('email', 'new@example.com')->first()));
    }

    public function test_register_rejects_duplicate_email(): void
    {
        $this->makeCustomer('taken@example.com');

        $this->expectException(ValidationException::class);

        $this->authService->register([
            'name' => 'Another Buyer',
            'email' => 'taken@example.com',
            'password' => 'secret1234',
        ]);
    }

    // ── login() ──────────────────────────────────────────────────────────────

    public function test_login_with_correct_credentials_issues_a_token(): void
    {
        $customer = $this->makeCustomer('login@example.com', 'correct-password');

        $token = $this->authService->login('login@example.com', 'correct-password');

        $this->assertNotFalse($token);
        $accessToken = PersonalAccessToken::findToken($token->plainTextToken);
        $this->assertTrue($accessToken->tokenable->is($customer));
    }

    public function test_login_with_wrong_password_fails(): void
    {
        $this->makeCustomer('login2@example.com', 'correct-password');

        $result = $this->authService->login('login2@example.com', 'wrong-password');

        $this->assertFalse($result);
    }

    public function test_login_updates_last_login_at(): void
    {
        $customer = $this->makeCustomer('login3@example.com', 'correct-password');
        $this->assertNull($customer->last_login_at);

        $this->authService->login('login3@example.com', 'correct-password');

        $this->assertNotNull($customer->fresh()->last_login_at);
    }

    // ── logout() ─────────────────────────────────────────────────────────────

    public function test_logout_revokes_the_current_access_token(): void
    {
        $customer = $this->makeCustomer('logout@example.com', 'correct-password');
        $token = $this->authService->login('logout@example.com', 'correct-password');
        $accessToken = PersonalAccessToken::findToken($token->plainTextToken);

        // Simulate the token that authenticated the current request.
        $customer->withAccessToken($accessToken);

        $this->authService->logout($customer);

        $this->assertNull(PersonalAccessToken::find($accessToken->id));
    }

    // ── guard wiring ─────────────────────────────────────────────────────────

    public function test_customer_guard_uses_sanctum_driver(): void
    {
        $this->assertSame('sanctum', config('auth.guards.customer.driver'));
        $this->assertSame('customers', config('auth.guards.customer.provider'));
    }

    public function test_authenticate_customer_middleware_allows_authenticated_requests(): void
    {
        $customer = $this->makeCustomer();
        Sanctum::actingAs($customer, [], 'customer');

        $response = (new AuthenticateCustomer)->handle(
            Request::create('/api/account/profile'),
            fn () => response()->json(['ok' => true]),
        );

        $this->assertSame(200, $response->getStatusCode());
    }

    public function test_authenticate_customer_middleware_rejects_unauthenticated_json_requests(): void
    {
        $request = Request::create('/api/account/profile');
        $request->headers->set('Accept', 'application/json');

        $response = (new AuthenticateCustomer)->handle(
            $request,
            fn () => response()->json(['ok' => true]),
        );

        $this->assertSame(401, $response->getStatusCode());
    }

    public function test_redirect_if_customer_authenticated_blocks_login_route_for_logged_in_customer(): void
    {
        $customer = $this->makeCustomer();
        Sanctum::actingAs($customer, [], 'customer');

        $request = Request::create('/api/account/login', 'POST');
        $request->headers->set('Accept', 'application/json');

        $response = (new RedirectIfCustomerAuthenticated)->handle(
            $request,
            fn () => response()->json(['ok' => true]),
        );

        $this->assertSame(200, $response->getStatusCode());
        $this->assertSame('Already authenticated.', $response->getData()->message);
    }
}
