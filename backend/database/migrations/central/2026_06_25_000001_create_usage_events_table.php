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
        Schema::connection('central')->create('usage_events', function (Blueprint $table) {
            $table->id();
            $table->foreignId('agency_id')->nullable()->constrained('agencies')->nullOnDelete();
            $table->string('tenant_id')->nullable();
            $table->foreignId('user_id')->nullable()->constrained('users')->nullOnDelete();
            $table->string('event_type');
            $table->string('event_group')->nullable();
            $table->string('subject_type')->nullable();
            $table->string('subject_id')->nullable();
            $table->jsonb('meta')->nullable();
            $table->timestamp('occurred_at');
            $table->timestamp('created_at')->useCurrent();

            $table->index(['event_type', 'occurred_at']);
            $table->index(['agency_id', 'occurred_at']);
            $table->index(['tenant_id', 'occurred_at']);
        });
    }

    public function down(): void
    {
        Schema::connection('central')->dropIfExists('usage_events');
    }
};
