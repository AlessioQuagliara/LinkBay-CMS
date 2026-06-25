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
        Schema::connection('central')->table('plugin_catalog_items', function (Blueprint $table) {
            $table->boolean('is_system')->default(false)->after('config')->index();
        });
    }

    public function down(): void
    {
        Schema::connection('central')->table('plugin_catalog_items', function (Blueprint $table) {
            $table->dropColumn('is_system');
        });
    }
};
