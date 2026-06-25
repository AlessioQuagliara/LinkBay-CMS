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
        Schema::connection('central')->create('agency_entitlements', function (Blueprint $table) {
            $table->id();
            $table->foreignId('agency_id')->constrained('agencies')->cascadeOnDelete();
            $table->foreignId('catalog_item_id')->constrained('plugin_catalog_items')->cascadeOnDelete();
            $table->string('source'); // plan | manual | promo | license
            $table->string('status')->default('active'); // active | expired | revoked
            $table->timestamp('starts_at')->nullable();
            $table->timestamp('ends_at')->nullable();
            $table->jsonb('metadata')->nullable();
            $table->timestamps();

            // One active entitlement per agency per item (prevent duplicates at DB level)
            $table->unique(['agency_id', 'catalog_item_id']);
            $table->index(['agency_id', 'status']);
            $table->index(['status', 'ends_at']);
        });
    }

    public function down(): void
    {
        Schema::connection('central')->dropIfExists('agency_entitlements');
    }
};
