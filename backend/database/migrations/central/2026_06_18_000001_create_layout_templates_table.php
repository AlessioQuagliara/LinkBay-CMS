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
        Schema::connection('central')->create('layout_templates', function (Blueprint $table) {
            $table->id();
            $table->foreignId('agency_id')->constrained('agencies')->cascadeOnDelete();
            $table->string('name');
            $table->string('slug');
            $table->string('status')->default('draft'); // draft | published
            $table->jsonb('blocks')->nullable();
            $table->timestamps();

            $table->unique(['agency_id', 'slug']);
            $table->index(['agency_id', 'status']);
        });
    }

    public function down(): void
    {
        Schema::connection('central')->dropIfExists('layout_templates');
    }
};
