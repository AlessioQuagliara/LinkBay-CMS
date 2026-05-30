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
        Schema::connection('central')->create('terms_acceptances', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('agency_id');
            $table->unsignedBigInteger('user_id');
            $table->string('terms_version', 20);      // es. "2026-01"
            $table->string('ip_address', 45);
            $table->text('user_agent')->nullable();
            $table->timestamp('accepted_at');
            // append-only: NO updated_at, NO soft delete

            $table->foreign('agency_id')->references('id')->on('agencies')->onDelete('cascade');
            $table->foreign('user_id')->references('id')->on('users')->onDelete('cascade');

            $table->unique(['agency_id', 'terms_version']);
            $table->index(['agency_id', 'accepted_at']);
        });
    }

    public function down(): void
    {
        Schema::connection('central')->dropIfExists('terms_acceptances');
    }
};
