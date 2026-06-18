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
        Schema::connection('central')->create('theme_presets', function (Blueprint $table) {
            $table->id();
            // NULL = system preset (visible to all agencies, not modifiable by them).
            // Non-null = agency-owned preset.
            $table->foreignId('agency_id')->nullable()->constrained('agencies')->cascadeOnDelete();
            $table->string('name');
            $table->string('slug');
            $table->string('status')->default('draft'); // draft | active
            $table->boolean('is_system')->default(false);
            $table->jsonb('config')->nullable();
            $table->timestamps();

            // Unique slug per agency (covers agency presets).
            // PostgreSQL treats (NULL, slug) pairs as distinct in unique indexes,
            // so system preset slug uniqueness is enforced at application level in the seeder.
            $table->unique(['agency_id', 'slug']);
            $table->index(['agency_id', 'status']);
            $table->index('is_system');
        });
    }

    public function down(): void
    {
        Schema::connection('central')->dropIfExists('theme_presets');
    }
};
