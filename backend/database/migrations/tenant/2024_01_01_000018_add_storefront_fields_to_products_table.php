<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('products', function (Blueprint $table) {
            $table->decimal('compare_at_price', 10, 2)->nullable()->after('compare_price');
            $table->decimal('cost_per_item', 10, 2)->nullable()->after('compare_at_price');
            $table->boolean('track_quantity')->default(true)->after('stock');
            $table->integer('quantity')->default(0)->after('track_quantity');
            $table->string('barcode')->nullable()->after('sku');
            $table->string('weight_unit')->default('kg')->after('weight');
            $table->boolean('requires_shipping')->default(true)->after('weight_unit');
            $table->boolean('is_taxable')->default(true)->after('requires_shipping');
            $table->string('tax_class')->nullable()->after('is_taxable');
            $table->string('seo_title')->nullable()->after('metadata');
            $table->text('seo_description')->nullable()->after('seo_title');
            $table->string('seo_keywords')->nullable()->after('seo_description');
        });
    }

    public function down(): void
    {
        Schema::table('products', function (Blueprint $table) {
            $table->dropColumn([
                'compare_at_price', 'cost_per_item', 'track_quantity', 'quantity',
                'barcode', 'weight_unit', 'requires_shipping', 'is_taxable',
                'tax_class', 'seo_title', 'seo_description', 'seo_keywords',
            ]);
        });
    }
};
