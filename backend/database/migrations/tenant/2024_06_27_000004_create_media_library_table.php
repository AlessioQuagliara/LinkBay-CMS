<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('media_library', function (Blueprint $table) {
            $table->id();
            $table->string('tenant_id');
            $table->string('name');
            $table->string('file_name');
            $table->string('mime_type');
            $table->string('disk')->default('tenant');
            $table->string('path');
            $table->unsignedBigInteger('size');
            $table->string('alt_text')->nullable();
            $table->string('title')->nullable();
            $table->string('collection')->nullable();
            $table->json('metadata')->nullable();
            $table->unsignedBigInteger('created_by')->nullable();
            $table->timestamps();

            // References the tenant's own 'users' table (App\Models\Tenant\User) —
            // there is no 'tenant_users' table; that string only appears elsewhere
            // as an auth guard/provider *name* (config/auth.php), not a table.
            // This FK previously pointed at a non-existent table, which is silently
            // tolerated by SQLite (used in tests) but hard-fails on Postgres (used
            // in Docker/production) with "relation tenant_users does not exist" —
            // found via live provisioning testing, 2026-07-09.
            $table->foreign('created_by')->references('id')->on('users')->nullOnDelete();
            $table->index(['tenant_id', 'collection']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('media_library');
    }
};
