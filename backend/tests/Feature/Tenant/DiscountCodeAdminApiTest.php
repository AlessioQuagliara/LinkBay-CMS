<?php

declare(strict_types=1);

namespace Tests\Feature\Tenant;

use App\Models\Tenant\DiscountCode;
use App\Models\Tenant\User as TenantUser;
use Illuminate\Auth\Middleware\Authenticate;
use Tests\Concerns\InteractsWithTenantRoutes;
use Tests\TenantTestCase;

/**
 * These admin CRUD routes sit behind the 'tenant_api' guard (config/auth.php),
 * a Sanctum guard pinned to the tenant_users provider — not the bare
 * 'auth:sanctum' default, which has no provider restriction and previously let
 * any Customer's own storefront token authenticate here too (App\Models\Tenant\User
 * is now the only tenant-DB model whose tokens satisfy this guard; see
 * test_customer_token_cannot_authenticate below). Business-logic tests bypass
 * the auth middleware directly; the two auth-focused tests at the bottom prove
 * the guard itself rejects unauthenticated/wrong-model requests and accepts
 * the right one.
 */
class DiscountCodeAdminApiTest extends TenantTestCase
{
    use InteractsWithTenantRoutes;

    protected function setUp(): void
    {
        parent::setUp();
        $this->bypassTenantDomainResolution();
    }

    private function bypassAuth(): void
    {
        $this->withoutMiddleware(Authenticate::class);
    }

    public function test_store_creates_discount_code_with_generated_code_when_omitted(): void
    {
        $this->bypassAuth();

        $response = $this->postJson('/api/v1/discount-codes', [
            'type' => 'percentage',
            'value' => 15,
        ]);

        $response->assertCreated();
        $this->assertDatabaseCount('discount_codes', 1);
        $this->assertNotEmpty($response->json('data.code'));
    }

    public function test_store_rejects_duplicate_code(): void
    {
        $this->bypassAuth();
        DiscountCode::factory()->create(['code' => 'DUPE10']);

        $response = $this->postJson('/api/v1/discount-codes', [
            'code' => 'DUPE10',
            'type' => 'fixed',
            'value' => 10,
        ]);

        $response->assertStatus(422);
        $response->assertJsonValidationErrors(['code']);
    }

    public function test_store_rejects_invalid_type(): void
    {
        $this->bypassAuth();

        $response = $this->postJson('/api/v1/discount-codes', [
            'type' => 'not_a_real_type',
            'value' => 10,
        ]);

        $response->assertStatus(422);
    }

    public function test_update_changes_value_and_active_flag(): void
    {
        $this->bypassAuth();
        $discount = DiscountCode::factory()->create(['value' => 10, 'is_active' => true]);

        $response = $this->putJson("/api/v1/discount-codes/{$discount->id}", [
            'value' => 25,
            'is_active' => false,
        ]);

        $response->assertOk();
        $fresh = $discount->fresh();
        $this->assertEquals(25, $fresh->value);
        $this->assertFalse($fresh->is_active);
    }

    public function test_destroy_deletes_discount_code(): void
    {
        $this->bypassAuth();
        $discount = DiscountCode::factory()->create();

        $response = $this->deleteJson("/api/v1/discount-codes/{$discount->id}");

        $response->assertOk();
        $this->assertDatabaseMissing('discount_codes', ['id' => $discount->id]);
    }

    public function test_index_requires_authentication(): void
    {
        $response = $this->getJson('/api/v1/discount-codes');

        $response->assertUnauthorized();
    }

    public function test_customer_token_cannot_authenticate(): void
    {
        $register = $this->postJson('/api/account/register', [
            'name' => 'Mario Rossi',
            'email' => 'mario@example.com',
            'password' => 'password123',
            'password_confirmation' => 'password123',
        ]);
        $token = $register->json('data.token');

        $response = $this->getJson('/api/v1/discount-codes', [
            'Authorization' => "Bearer {$token}",
        ]);

        $response->assertUnauthorized();
    }

    public function test_tenant_user_token_authenticates(): void
    {
        $user = TenantUser::factory()->create();
        $token = $user->createToken('test')->plainTextToken;
        DiscountCode::factory()->create();

        $response = $this->getJson('/api/v1/discount-codes', [
            'Authorization' => "Bearer {$token}",
        ]);

        $response->assertOk();
    }
}
