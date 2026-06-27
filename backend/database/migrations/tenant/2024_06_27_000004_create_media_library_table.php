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

            $table->foreign('created_by')->references('id')->on('tenant_users')->nullOnDelete();
            $table->index(['tenant_id', 'collection']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('media_library');
    }
};
