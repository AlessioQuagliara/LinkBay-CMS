<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('store_payment_settings', function (Blueprint $table) {
            $table->id();
            $table->string('stripe_account_id')->nullable();
            $table->string('stripe_publishable_key')->nullable();
            $table->text('stripe_secret_key')->nullable();
            // stripe_secret_key is stored encrypted via Model cast
            $table->json('payment_methods_enabled')->default('["card"]');
            $table->string('currency', 3)->default('eur');
            $table->string('capture_method', 20)->default('automatic');
            // capture_method: automatic | manual
            $table->string('statement_descriptor', 22)->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('store_payment_settings');
    }
};
