<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('discount_codes', function (Blueprint $table) {
            $table->id();
            $table->string('code')->unique();
            $table->string('type')->default('percentage');
            $table->decimal('value', 10, 2)->default(0);
            $table->integer('usage_limit')->nullable();
            $table->integer('used_count')->default(0);
            $table->decimal('minimum_amount', 10, 2)->nullable();
            $table->timestamp('expires_at')->nullable();
            $table->boolean('is_active')->default(true);
            $table->json('applies_to')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('discount_codes');
    }
};
