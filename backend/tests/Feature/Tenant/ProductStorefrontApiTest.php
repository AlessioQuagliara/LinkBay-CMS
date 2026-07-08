<?php

declare(strict_types=1);

namespace Tests\Feature\Tenant;

use App\Models\Tenant\Product;
use Tests\Concerns\InteractsWithTenantRoutes;
use Tests\TenantTestCase;

class ProductStorefrontApiTest extends TenantTestCase
{
    use InteractsWithTenantRoutes;

    protected function setUp(): void
    {
        parent::setUp();
        $this->bypassTenantDomainResolution();
    }

    public function test_storefront_lists_only_active_products(): void
    {
        Product::factory()->create(['name' => 'Visible Product']);
        Product::factory()->inactive()->create(['name' => 'Hidden Product']);

        $response = $this->getJson('/api/store/products');

        $response->assertOk();
        $names = collect($response->json('data'))->pluck('name');
        $this->assertTrue($names->contains('Visible Product'));
        $this->assertFalse($names->contains('Hidden Product'));
    }

    public function test_storefront_search_matches_name_and_sku(): void
    {
        Product::factory()->create(['name' => 'Blue Ceramic Mug', 'sku' => 'MUG-BLUE']);
        Product::factory()->create(['name' => 'Red Notebook', 'sku' => 'NB-RED']);

        $response = $this->getJson('/api/store/products?q=Ceramic');

        $response->assertOk();
        $names = collect($response->json('data'))->pluck('name');
        $this->assertTrue($names->contains('Blue Ceramic Mug'));
        $this->assertFalse($names->contains('Red Notebook'));
    }

    public function test_storefront_filters_by_price_range(): void
    {
        Product::factory()->create(['name' => 'Cheap Item', 'price' => 5]);
        Product::factory()->create(['name' => 'Mid Item', 'price' => 50]);
        Product::factory()->create(['name' => 'Expensive Item', 'price' => 500]);

        $response = $this->getJson('/api/store/products?min_price=10&max_price=100');

        $response->assertOk();
        $names = collect($response->json('data'))->pluck('name');
        $this->assertSame(['Mid Item'], $names->values()->all());
    }

    public function test_storefront_in_stock_filter_excludes_zero_stock_products(): void
    {
        Product::factory()->create(['name' => 'In Stock', 'stock' => 5]);
        Product::factory()->outOfStock()->create(['name' => 'Sold Out']);

        $response = $this->getJson('/api/store/products?in_stock=1');

        $response->assertOk();
        $names = collect($response->json('data'))->pluck('name');
        $this->assertTrue($names->contains('In Stock'));
        $this->assertFalse($names->contains('Sold Out'));
    }

    public function test_product_detail_by_slug_returns_full_product(): void
    {
        $product = Product::factory()->create(['name' => 'Detail Product', 'slug' => 'detail-product']);

        $response = $this->getJson('/api/store/products/detail-product');

        $response->assertOk();
        $response->assertJsonPath('data.id', $product->id);
        $response->assertJsonPath('data.name', 'Detail Product');
    }

    public function test_product_detail_returns_404_for_unknown_slug(): void
    {
        $response = $this->getJson('/api/store/products/does-not-exist');

        $response->assertNotFound();
    }
}
