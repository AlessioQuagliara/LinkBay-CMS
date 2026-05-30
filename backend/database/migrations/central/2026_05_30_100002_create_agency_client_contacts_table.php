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
        Schema::connection('central')->create('agency_client_contacts', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('agency_client_id');
            $table->unsignedBigInteger('user_id')->nullable();
            $table->string('name');
            $table->string('email');
            $table->string('role', 100)->nullable();
            $table->boolean('can_access_tenant')->default(false);
            $table->timestamps();

            $table->foreign('agency_client_id')
                ->references('id')->on('agency_clients')->onDelete('cascade');
            $table->index('agency_client_id');
        });
    }

    public function down(): void
    {
        Schema::connection('central')->dropIfExists('agency_client_contacts');
    }
};
