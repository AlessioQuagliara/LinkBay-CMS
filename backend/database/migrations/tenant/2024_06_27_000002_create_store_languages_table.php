<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('store_languages', function (Blueprint $table) {
            $table->id();
            $table->string('tenant_id');
            $table->string('locale', 10);
            $table->boolean('is_default')->default(false);
            $table->boolean('is_active')->default(true);
            $table->timestamps();

            $table->unique(['tenant_id', 'locale']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('store_languages');
    }
};
