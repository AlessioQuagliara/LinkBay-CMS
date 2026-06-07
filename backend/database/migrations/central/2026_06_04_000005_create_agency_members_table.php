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
        Schema::connection('central')->create('agency_members', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('agency_id');
            $table->unsignedBigInteger('user_id')->nullable(); // null until invite accepted
            $table->string('role')->default('member');         // owner | admin | member
            $table->unsignedBigInteger('invited_by_user_id')->nullable();
            $table->string('invited_email')->nullable();       // email used when invite was sent
            $table->timestamp('invited_at')->nullable();
            $table->timestamp('accepted_at')->nullable();
            $table->string('status')->default('pending');      // pending | active | suspended
            $table->string('invite_token', 64)->nullable()->unique();
            $table->timestamp('invite_expires_at')->nullable();
            $table->timestamps();

            $table->foreign('agency_id')->references('id')->on('agencies')->cascadeOnDelete();
            $table->foreign('user_id')->references('id')->on('users')->nullOnDelete();
            $table->foreign('invited_by_user_id')->references('id')->on('users')->nullOnDelete();

            $table->index(['agency_id', 'status']);
            $table->index(['agency_id', 'user_id']);
        });
    }

    public function down(): void
    {
        Schema::connection('central')->dropIfExists('agency_members');
    }
};
