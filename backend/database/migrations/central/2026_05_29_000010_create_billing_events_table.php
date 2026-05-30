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
        Schema::connection('central')->create('billing_events', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('agency_id')->nullable();
            $table->string('tenant_id')->nullable();
            $table->string('stripe_event_id')->nullable()->unique();  // idempotenza
            $table->string('event_type');
            $table->jsonb('payload');
            $table->timestamp('processed_at')->nullable();
            $table->text('error')->nullable();
            $table->timestamp('created_at')->useCurrent();
            // NO updated_at

            $table->foreign('agency_id')->references('id')->on('agencies')->onDelete('set null');

            $table->index(['event_type', 'processed_at']);
            $table->index('created_at');
        });
    }

    public function down(): void
    {
        Schema::connection('central')->dropIfExists('billing_events');
    }
};
