<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('checkout_sessions', function (Blueprint $table) {
            $table->id();
            $table->foreignId('cart_session_id')->constrained()->cascadeOnDelete();
            $table->foreignId('customer_id')->nullable()->constrained()->nullOnDelete();
            $table->enum('status', ['pending', 'processing', 'completed', 'abandoned'])->default('pending');
            $table->json('shipping_address')->nullable();
            $table->json('billing_address')->nullable();
            $table->foreignId('shipping_method_id')->nullable()->constrained()->nullOnDelete();
            $table->foreignId('discount_code_id')->nullable()->constrained()->nullOnDelete();
            $table->decimal('subtotal', 10, 2)->default(0);
            $table->decimal('shipping_amount', 10, 2)->default(0);
            $table->decimal('discount_amount', 10, 2)->default(0);
            $table->decimal('tax_amount', 10, 2)->default(0);
            $table->decimal('total', 10, 2)->default(0);
            $table->string('stripe_payment_intent_id')->nullable();
            $table->string('stripe_payment_status')->nullable();
            $table->timestamp('completed_at')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('checkout_sessions');
    }
};
