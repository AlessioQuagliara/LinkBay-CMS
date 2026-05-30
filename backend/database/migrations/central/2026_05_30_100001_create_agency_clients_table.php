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
        Schema::connection('central')->create('agency_clients', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('agency_id');
            $table->string('name');
            $table->string('legal_name')->nullable();
            $table->string('vat_number', 30)->nullable();
            $table->string('country', 2)->nullable();
            $table->string('billing_email')->nullable();
            $table->string('status', 20)->default('active'); // active | suspended | offboarded
            $table->text('notes')->nullable();
            $table->timestamps();

            $table->foreign('agency_id')->references('id')->on('agencies')->onDelete('cascade');
            $table->index('agency_id');
        });
    }

    public function down(): void
    {
        Schema::connection('central')->dropIfExists('agency_clients');
    }
};
