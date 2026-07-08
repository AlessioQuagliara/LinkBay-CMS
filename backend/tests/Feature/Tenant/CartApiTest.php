<?php

declare(strict_types=1);

namespace Tests\Feature\Tenant;

use App\Models\Tenant\CartItem;
use App\Models\Tenant\CartSession;
use App\Models\Tenant\DiscountCode;
use App\Models\Tenant\Product;
use Tests\Concerns\InteractsWithTenantRoutes;
use Tests\TenantTestCase;

class CartApiTest extends TenantTestCase
{
    use InteractsWithTenantRoutes;

    protected function setUp(): void
    {
        parent::setUp();
        $this->bypassTenantDomainResolution();
    }

    public function test_store_creates_a_new_cart_session(): void
    {
        $response = $this->postJson('/api/store/cart', ['session_id' => 'sess-1']);

        $response->assertCreated();
        $this->assertDatabaseHas('cart_sessions', ['session_id' => 'sess-1']);
    }

    public function test_add_item_creates_cart_item_with_product_price(): void
    {
        $cart = CartSession::factory()->create();
        $product = Product::factory()->create(['price' => 19.99]);

        $response = $this->postJson("/api/store/cart/{$cart->session_id}/items", [
            'product_id' => $product->id,
            'quantity' => 2,
        ]);

        $response->assertCreated();
        $this->assertDatabaseHas('cart_items', [
            'cart_session_id' => $cart->id,
            'product_id' => $product->id,
            'quantity' => 2,
            'unit_price' => 19.99,
        ]);
        $this->assertSame(39.98, $response->json('meta.subtotal'));
    }

    public function test_add_item_twice_increments_quantity_instead_of_duplicating(): void
    {
        $cart = CartSession::factory()->create();
        $product = Product::factory()->create(['price' => 10]);

        $this->postJson("/api/store/cart/{$cart->session_id}/items", ['product_id' => $product->id, 'quantity' => 1]);
        $this->postJson("/api/store/cart/{$cart->session_id}/items", ['product_id' => $product->id, 'quantity' => 3]);

        $this->assertSame(1, CartItem::where('cart_session_id', $cart->id)->count());
        $this->assertSame(4, CartItem::where('cart_session_id', $cart->id)->first()->quantity);
    }

    public function test_add_item_rejects_nonexistent_product(): void
    {
        $cart = CartSession::factory()->create();

        $response = $this->postJson("/api/store/cart/{$cart->session_id}/items", [
            'product_id' => 999999,
            'quantity' => 1,
        ]);

        $response->assertUnprocessable();
    }

    public function test_update_item_changes_quantity(): void
    {
        $cart = CartSession::factory()->create();
        $item = CartItem::factory()->create(['cart_session_id' => $cart->id, 'quantity' => 1]);

        $response = $this->patchJson("/api/store/cart/{$cart->session_id}/items/{$item->id}", ['quantity' => 5]);

        $response->assertOk();
        $this->assertSame(5, $item->fresh()->quantity);
    }

    public function test_update_item_from_a_different_cart_is_forbidden(): void
    {
        $ownCart = CartSession::factory()->create();
        $otherCart = CartSession::factory()->create();
        $itemInOtherCart = CartItem::factory()->create(['cart_session_id' => $otherCart->id]);

        $response = $this->patchJson("/api/store/cart/{$ownCart->session_id}/items/{$itemInOtherCart->id}", ['quantity' => 5]);

        $response->assertForbidden();
    }

    public function test_remove_item_deletes_it_and_updates_summary(): void
    {
        $cart = CartSession::factory()->create();
        $item = CartItem::factory()->create(['cart_session_id' => $cart->id, 'quantity' => 1, 'unit_price' => 10]);

        $response = $this->deleteJson("/api/store/cart/{$cart->session_id}/items/{$item->id}");

        $response->assertOk();
        $this->assertDatabaseMissing('cart_items', ['id' => $item->id]);
        $this->assertEquals(0, $response->json('meta.subtotal'));
    }

    public function test_remove_item_from_a_different_cart_is_forbidden(): void
    {
        $ownCart = CartSession::factory()->create();
        $otherCart = CartSession::factory()->create();
        $itemInOtherCart = CartItem::factory()->create(['cart_session_id' => $otherCart->id]);

        $response = $this->deleteJson("/api/store/cart/{$ownCart->session_id}/items/{$itemInOtherCart->id}");

        $response->assertForbidden();
        $this->assertDatabaseHas('cart_items', ['id' => $itemInOtherCart->id]);
    }

    public function test_apply_discount_succeeds_for_valid_code(): void
    {
        $cart = CartSession::factory()->create();
        CartItem::factory()->create(['cart_session_id' => $cart->id, 'quantity' => 1, 'unit_price' => 100]);
        DiscountCode::factory()->create(['code' => 'SAVE10']);

        $response = $this->postJson("/api/store/cart/{$cart->session_id}/discount", ['code' => 'save10']);

        $response->assertOk();
        $this->assertTrue($response->json('meta.success'));
        $response->assertJsonPath('data.code', 'SAVE10');
    }

    public function test_apply_discount_fails_for_unknown_code(): void
    {
        $cart = CartSession::factory()->create();

        $response = $this->postJson("/api/store/cart/{$cart->session_id}/discount", ['code' => 'NOPE']);

        $response->assertStatus(422);
        $this->assertFalse($response->json('meta.success'));
    }

    public function test_apply_discount_fails_for_expired_code(): void
    {
        $cart = CartSession::factory()->create();
        DiscountCode::factory()->expired()->create(['code' => 'OLDCODE']);

        $response = $this->postJson("/api/store/cart/{$cart->session_id}/discount", ['code' => 'OLDCODE']);

        $response->assertStatus(422);
    }

    public function test_apply_discount_fails_when_below_minimum_amount(): void
    {
        $cart = CartSession::factory()->create();
        CartItem::factory()->create(['cart_session_id' => $cart->id, 'quantity' => 1, 'unit_price' => 5]);
        DiscountCode::factory()->create(['code' => 'MIN50', 'minimum_amount' => 50]);

        $response = $this->postJson("/api/store/cart/{$cart->session_id}/discount", ['code' => 'MIN50']);

        $response->assertStatus(422);
        $this->assertFalse($response->json('meta.success'));
    }
}
