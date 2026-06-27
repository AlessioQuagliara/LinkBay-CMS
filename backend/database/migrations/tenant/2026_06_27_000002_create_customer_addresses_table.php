<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('customer_addresses', function (Blueprint $table) {
            $table->id();
            $table->foreignId('customer_id')->constrained('customers')->cascadeOnDelete();
            $table->string('label')->nullable();
            $table->string('first_name');
            $table->string('last_name');
            $table->string('company')->nullable();
            $table->string('address_line_1');
            $table->string('address_line_2')->nullable();
            $table->string('city');
            $table->string('state')->nullable();
            $table->string('postal_code');
            $table->char('country_code', 2);
            $table->string('phone')->nullable();
            $table->boolean('is_default_shipping')->default(false);
            $table->boolean('is_default_billing')->default(false);
            $table->timestamps();
        });

        // FK from customers back to addresses (added after table exists)
        Schema::table('customers', function (Blueprint $table) {
            $table->foreign('default_shipping_address_id')
                ->references('id')->on('customer_addresses')
                ->nullOnDelete();
            $table->foreign('default_billing_address_id')
                ->references('id')->on('customer_addresses')
                ->nullOnDelete();
        });
    }

    public function down(): void
    {
        Schema::table('customers', function (Blueprint $table) {
            $table->dropForeign(['default_shipping_address_id']);
            $table->dropForeign(['default_billing_address_id']);
        });

        Schema::dropIfExists('customer_addresses');
    }
};
