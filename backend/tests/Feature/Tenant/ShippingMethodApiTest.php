<?php

declare(strict_types=1);

namespace Tests\Feature\Tenant;

use App\Models\Tenant\ShippingMethod;
use Tests\Concerns\InteractsWithTenantRoutes;
use Tests\TenantTestCase;

class ShippingMethodApiTest extends TenantTestCase
{
    use InteractsWithTenantRoutes;

    protected function setUp(): void
    {
        parent::setUp();
        $this->bypassTenantDomainResolution();
    }

    public function test_index_returns_only_active_methods_ordered_by_price(): void
    {
        ShippingMethod::factory()->create(['name' => 'Express', 'price' => 15, 'is_active' => true]);
        ShippingMethod::factory()->create(['name' => 'Standard', 'price' => 5, 'is_active' => true]);
        ShippingMethod::factory()->inactive()->create(['name' => 'Discontinued', 'price' => 1]);

        $response = $this->getJson('/api/store/shipping-methods');

        $response->assertOk();
        $names = collect($response->json('data'))->pluck('name')->values()->all();
        $this->assertSame(['Standard', 'Express'], $names);
    }

    public function test_index_returns_empty_when_no_active_methods(): void
    {
        ShippingMethod::factory()->inactive()->create();

        $response = $this->getJson('/api/store/shipping-methods');

        $response->assertOk();
        $this->assertCount(0, $response->json('data'));
    }
}
