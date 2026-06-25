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
        Schema::connection('central')->create('agency_health_alerts', function (Blueprint $table) {
            $table->id();
            $table->foreignId('agency_id')->constrained('agencies')->cascadeOnDelete();
            $table->string('type');
            $table->string('severity');
            $table->timestamp('detected_at');
            $table->timestamp('resolved_at')->nullable();
            $table->jsonb('meta')->nullable();
            $table->timestamps();

            $table->index(['agency_id', 'type', 'resolved_at']);
            $table->index(['resolved_at']);
            $table->index(['detected_at']);
        });
    }

    public function down(): void
    {
        Schema::connection('central')->dropIfExists('agency_health_alerts');
    }
};
