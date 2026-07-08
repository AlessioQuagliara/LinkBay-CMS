<?php

declare(strict_types=1);

namespace Tests\Feature\Tenant;

use App\Models\Tenant\CartItem;
use App\Models\Tenant\CartSession;
use App\Models\Tenant\Customer;
use App\Models\Tenant\Order;
use App\Models\Tenant\Product;
use Tests\TenantIsolationTestCase;

/**
 * Proves real DB-per-tenant isolation for the commerce models, using two
 * independent physical SQLite connections (see TenantIsolationTestCase).
 *
 * Unlike StorefrontFeaturesApiTest (which proves column-level scoping on the
 * shared central DB), these tests prove that store A's data is not merely
 * filtered out but literally does not exist in store B's database.
 */
class TenantIsolationTest extends TenantIsolationTestCase
{
    protected function setUp(): void
    {
        parent::setUp();

        $this->defineTenantConnection('tenant_a');
        $this->defineTenantConnection('tenant_b');
    }

    public function test_products_do_not_leak_between_tenants(): void
    {
        $this->asTenant('tenant_a', fn () => Product::factory()->create(['name' => 'Tenant A Widget']));
        $this->asTenant('tenant_b', fn () => Product::factory()->create(['name' => 'Tenant B Gadget']));

        $this->asTenant('tenant_a', function () {
            $this->assertSame(1, Product::count());
            $this->assertTrue(Product::where('name', 'Tenant A Widget')->exists());
            $this->assertFalse(Product::where('name', 'Tenant B Gadget')->exists());
        });

        $this->asTenant('tenant_b', function () {
            $this->assertSame(1, Product::count());
            $this->assertTrue(Product::where('name', 'Tenant B Gadget')->exists());
            $this->assertFalse(Product::where('name', 'Tenant A Widget')->exists());
        });
    }

    public function test_same_email_can_register_as_customer_in_two_different_tenants(): void
    {
        $email = 'shared-customer@example.com';

        $this->asTenant('tenant_a', fn () => Customer::factory()->create(['email' => $email, 'name' => 'Customer A']));
        $this->asTenant('tenant_b', fn () => Customer::factory()->create(['email' => $email, 'name' => 'Customer B']));

        $this->asTenant('tenant_a', function () use ($email) {
            $this->assertSame(1, Customer::where('email', $email)->count());
            $this->assertSame('Customer A', Customer::where('email', $email)->first()->name);
        });

        $this->asTenant('tenant_b', function () use ($email) {
            $this->assertSame(1, Customer::where('email', $email)->count());
            $this->assertSame('Customer B', Customer::where('email', $email)->first()->name);
        });
    }

    public function test_orders_do_not_leak_between_tenants(): void
    {
        $this->asTenant('tenant_a', fn () => Order::factory()->count(3)->create());
        $this->asTenant('tenant_b', fn () => Order::factory()->count(1)->create());

        $this->asTenant('tenant_a', fn () => $this->assertSame(3, Order::count()));
        $this->asTenant('tenant_b', fn () => $this->assertSame(1, Order::count()));
    }

    public function test_cart_sessions_with_the_same_session_id_do_not_collide_across_tenants(): void
    {
        $sharedSessionId = 'guest-session-shared-id';

        $this->asTenant('tenant_a', function () use ($sharedSessionId) {
            $cart = CartSession::factory()->create(['session_id' => $sharedSessionId]);
            CartItem::factory()->count(2)->create(['cart_session_id' => $cart->id]);
        });

        $this->asTenant('tenant_b', function () use ($sharedSessionId) {
            $cart = CartSession::factory()->create(['session_id' => $sharedSessionId]);
            CartItem::factory()->count(1)->create(['cart_session_id' => $cart->id]);
        });

        $this->asTenant('tenant_a', function () use ($sharedSessionId) {
            $cart = CartSession::where('session_id', $sharedSessionId)->firstOrFail();
            $this->assertSame(2, $cart->cartItems()->count());
        });

        $this->asTenant('tenant_b', function () use ($sharedSessionId) {
            $cart = CartSession::where('session_id', $sharedSessionId)->firstOrFail();
            $this->assertSame(1, $cart->cartItems()->count());
        });
    }
}
