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
        Schema::connection('central')->create('layout_assignments', function (Blueprint $table) {
            $table->id();
            $table->foreignId('agency_id')->constrained('agencies')->cascadeOnDelete();
            $table->string('tenant_id');
            $table->foreignId('layout_template_id')->constrained('layout_templates')->cascadeOnDelete();
            // page_key identifies which page slot this layout occupies (home, landing, about…)
            $table->string('page_key')->default('home');
            $table->timestamps();

            // One active template per page slot per store.
            $table->unique(['tenant_id', 'page_key']);
            $table->index('agency_id');

            $table->foreign('tenant_id')->references('id')->on('tenants')->cascadeOnDelete();
        });
    }

    public function down(): void
    {
        Schema::connection('central')->dropIfExists('layout_assignments');
    }
};
