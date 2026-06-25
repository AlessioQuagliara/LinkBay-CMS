<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * Sprint 1 performance indices.
 *
 * usage_events: composite (event_type, agency_id, occurred_at) covers batchActiveTenants()
 *   which filters all three columns — the existing (event_type, occurred_at) and
 *   (agency_id, occurred_at) indices cannot be used together by the planner.
 *
 * theme_presets: index on parent_theme_slug for fork lookups.
 */
return new class extends Migration
{
    protected $connection = 'central';

    public function up(): void
    {
        Schema::connection('central')->table('usage_events', function (Blueprint $table) {
            $table->index(['event_type', 'agency_id', 'occurred_at'], 'usage_events_type_agency_occurred_idx');
        });

        Schema::connection('central')->table('theme_presets', function (Blueprint $table) {
            $table->index('parent_theme_slug', 'theme_presets_parent_slug_idx');
        });
    }

    public function down(): void
    {
        Schema::connection('central')->table('usage_events', function (Blueprint $table) {
            $table->dropIndex('usage_events_type_agency_occurred_idx');
        });

        Schema::connection('central')->table('theme_presets', function (Blueprint $table) {
            $table->dropIndex('theme_presets_parent_slug_idx');
        });
    }
};
