<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('shipping_methods', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('carrier')->nullable();
            $table->decimal('price', 10, 2)->default(0);
            $table->json('rules')->nullable();
            $table->boolean('is_active')->default(true);
            $table->integer('estimated_days')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('shipping_methods');
    }
};
