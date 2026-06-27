<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('orders', function (Blueprint $table) {
            $table->index('created_at', 'idx_orders_created_at');
            $table->index('status', 'idx_orders_status');
        });

        Schema::table('order_items', function (Blueprint $table) {
            $table->index('product_id', 'idx_order_items_product_id');
        });

        Schema::table('products', function (Blueprint $table) {
            $table->index('is_active', 'idx_products_is_active');
            $table->index(['is_active', 'stock'], 'idx_products_active_stock');
            $table->index(['is_active', 'quantity'], 'idx_products_active_quantity');
        });
    }

    public function down(): void
    {
        Schema::table('orders', function (Blueprint $table) {
            $table->dropIndex('idx_orders_created_at');
            $table->dropIndex('idx_orders_status');
        });

        Schema::table('order_items', function (Blueprint $table) {
            $table->dropIndex('idx_order_items_product_id');
        });

        Schema::table('products', function (Blueprint $table) {
            $table->dropIndex('idx_products_is_active');
            $table->dropIndex('idx_products_active_stock');
            $table->dropIndex('idx_products_active_quantity');
        });
    }
};
