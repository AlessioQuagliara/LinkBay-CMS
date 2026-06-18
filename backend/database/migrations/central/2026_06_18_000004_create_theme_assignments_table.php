<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    protected $connection = 'central';

    public function up(): void
    {
        Schema::connection('central')->create('theme_assignments', function (Blueprint $table) {
            $table->id();
            $table->foreignId('agency_id')->constrained('agencies')->cascadeOnDelete();
            // String FK: tenants.id is a string (stancl/tenancy convention).
            $table->string('tenant_id');
            $table->foreignId('theme_preset_id')->constrained('theme_presets')->cascadeOnDelete();
            $table->timestamps();

            // One active theme per store.
            $table->unique('tenant_id');
            $table->foreign('tenant_id')->references('id')->on('tenants')->cascadeOnDelete();
            $table->index('agency_id');
            $table->index('theme_preset_id');
        });
    }

    public function down(): void
    {
        Schema::connection('central')->dropIfExists('theme_assignments');
    }
};
