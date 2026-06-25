<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

/**
 * Fase 4D — Fork-with-Lock: add fork tracking columns to theme_presets.
 *
 * parent_theme_slug: slug of the system theme in the PluginRegistry this preset forks from.
 *                   Null = standalone preset (no inheritance).
 * override_config:  JSON of only the fields the agency has customized.
 *                   Empty/null = inherits all values from parent.
 *
 * The resolved config (parent base + overrides) is computed at read time
 * via ThemePreset::resolvedConfig(). section_style and header_style are
 * always locked to the parent value regardless of override_config contents.
 */
return new class extends Migration
{
    public function getConnection(): string
    {
        return 'central';
    }

    public function up(): void
    {
        Schema::connection('central')->table('theme_presets', function (Blueprint $table) {
            $table->string('parent_theme_slug')->nullable()->after('agency_id');
            $table->jsonb('override_config')->nullable()->after('config');
        });
    }

    public function down(): void
    {
        Schema::connection('central')->table('theme_presets', function (Blueprint $table) {
            $table->dropColumn(['parent_theme_slug', 'override_config']);
        });
    }
};
