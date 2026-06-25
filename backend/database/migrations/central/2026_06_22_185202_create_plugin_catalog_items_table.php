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
        Schema::connection('central')->create('plugin_catalog_items', function (Blueprint $table) {
            $table->id();
            $table->string('code')->unique();
            $table->string('type'); // feature | theme_pack | block_pack | plugin
            $table->string('name');
            $table->text('description')->nullable();
            $table->string('status')->default('draft'); // draft | active | archived
            $table->jsonb('config')->nullable();
            $table->timestamps();

            $table->index(['type', 'status']);
        });
    }

    public function down(): void
    {
        Schema::connection('central')->dropIfExists('plugin_catalog_items');
    }
};
