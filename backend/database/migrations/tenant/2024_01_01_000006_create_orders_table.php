<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('orders', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('customer_id');
            $table->string('status')->default('pending');
            $table->decimal('total', 12, 2)->default(0);
            $table->decimal('subtotal', 12, 2)->default(0);
            $table->decimal('discount_total', 10, 2)->default(0);
            $table->decimal('shipping_total', 10, 2)->default(0);
            $table->unsignedBigInteger('shipping_method_id')->nullable();
            $table->string('payment_method')->nullable();
            $table->string('payment_status')->default('pending');
            $table->string('tracking_number')->nullable();
            $table->text('notes')->nullable();
            $table->json('shipping_address')->nullable();
            $table->json('billing_address')->nullable();
            $table->unsignedBigInteger('discount_code_id')->nullable();
            $table->json('metadata')->nullable();
            $table->timestamps();

            $table->foreign('customer_id')->references('id')->on('customers')->onDelete('restrict');
            $table->foreign('shipping_method_id')->references('id')->on('shipping_methods')->onDelete('set null');
            $table->foreign('discount_code_id')->references('id')->on('discount_codes')->onDelete('set null');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('orders');
    }
};
