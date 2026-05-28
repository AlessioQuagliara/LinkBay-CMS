<?php

declare(strict_types=1);

namespace Database\Seeders;

use App\Models\Tenant\Collection;
use App\Models\Tenant\Customer;
use App\Models\Tenant\DiscountCode;
use App\Models\Tenant\Order;
use App\Models\Tenant\OrderItem;
use App\Models\Tenant\Page;
use App\Models\Tenant\Product;
use App\Models\Tenant\Setting;
use App\Models\Tenant\ShippingMethod;
use Illuminate\Database\Seeder;

class TenantSeeder extends Seeder
{
    public function run(): void
    {
        // Collections
        $root = Collection::create(['name' => 'Tutti i prodotti', 'slug' => 'tutti-i-prodotti', 'is_active' => true]);
        $abbigliamento = Collection::create(['name' => 'Abbigliamento', 'slug' => 'abbigliamento', 'parent_id' => $root->id, 'is_active' => true]);
        $accessori = Collection::create(['name' => 'Accessori', 'slug' => 'accessori', 'parent_id' => $root->id, 'is_active' => true]);

        // Products
        $p1 = Product::create([
            'name' => 'T-Shirt Classic',
            'slug' => 't-shirt-classic',
            'description' => 'T-shirt in cotone 100% biologico.',
            'price' => 19.99,
            'stock' => 100,
            'sku' => 'TSH-001',
            'collection_id' => $abbigliamento->id,
            'images' => ['https://via.placeholder.com/400x400?text=T-Shirt'],
            'is_active' => true,
        ]);

        $p2 = Product::create([
            'name' => 'Cappello Snapback',
            'slug' => 'cappello-snapback',
            'description' => 'Cappello regolabile con logo ricamato.',
            'price' => 24.99,
            'stock' => 50,
            'sku' => 'CAP-001',
            'collection_id' => $accessori->id,
            'images' => ['https://via.placeholder.com/400x400?text=Cappello'],
            'is_active' => true,
        ]);

        // Shipping Methods
        $shipping = ShippingMethod::create([
            'name' => 'Spedizione Standard',
            'carrier' => 'BRT',
            'price' => 4.99,
            'is_active' => true,
            'estimated_days' => 3,
        ]);

        ShippingMethod::create([
            'name' => 'Spedizione Express',
            'carrier' => 'DHL',
            'price' => 9.99,
            'is_active' => true,
            'estimated_days' => 1,
        ]);

        // Discount Code
        DiscountCode::create([
            'code' => 'BENVENUTO10',
            'type' => 'percentage',
            'value' => 10,
            'usage_limit' => 100,
            'is_active' => true,
        ]);

        // Customers
        $customer = Customer::create([
            'name' => 'Mario Rossi',
            'email' => 'mario.rossi@esempio.it',
            'phone' => '+39 333 1234567',
            'address' => [
                'street' => 'Via Roma 1',
                'city' => 'Milano',
                'zip' => '20100',
                'province' => 'MI',
                'country' => 'IT',
            ],
        ]);

        // Demo Order
        $order = Order::create([
            'customer_id' => $customer->id,
            'status' => 'delivered',
            'subtotal' => 44.98,
            'shipping_total' => 4.99,
            'total' => 49.97,
            'shipping_method_id' => $shipping->id,
            'payment_method' => 'stripe',
            'payment_status' => 'paid',
        ]);

        OrderItem::create(['order_id' => $order->id, 'product_id' => $p1->id, 'name' => $p1->name, 'sku' => $p1->sku, 'quantity' => 1, 'price' => 19.99, 'total' => 19.99]);
        OrderItem::create(['order_id' => $order->id, 'product_id' => $p2->id, 'name' => $p2->name, 'sku' => $p2->sku, 'quantity' => 1, 'price' => 24.99, 'total' => 24.99]);

        // Pages
        Page::create(['slug' => 'homepage', 'title' => 'Home', 'content' => ['hero' => ['title' => 'Benvenuto nel nostro negozio']], 'is_published' => true]);
        Page::create(['slug' => 'chi-siamo', 'title' => 'Chi Siamo', 'content' => ['body' => 'La nostra storia...'], 'is_published' => true]);

        // Settings
        Setting::set('currency', 'EUR');
        Setting::set('currency_symbol', '€');
        Setting::set('timezone', 'Europe/Rome');
        Setting::set('locale', 'it');
        Setting::set('tax_rate', 22);
        Setting::set('free_shipping_threshold', 50);

        $this->command->info('Tenant seeder: dati demo caricati.');
    }
}
