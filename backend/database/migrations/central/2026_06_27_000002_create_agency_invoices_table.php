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
        Schema::connection('central')->create('agency_invoices', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('agency_id');
            $table->string('stripe_invoice_id')->unique();
            $table->unsignedInteger('amount_due');
            $table->unsignedInteger('amount_paid');
            $table->string('currency', 3)->default('eur');
            $table->string('status', 20);
            // status: paid | open | void | uncollectible
            $table->string('invoice_pdf_url')->nullable();
            $table->timestamp('period_start')->nullable();
            $table->timestamp('period_end')->nullable();
            $table->timestamp('paid_at')->nullable();
            $table->json('line_items')->nullable();
            $table->timestamps();

            $table->foreign('agency_id')->references('id')->on('agencies')->onDelete('cascade');
            $table->index(['agency_id', 'created_at']);
        });
    }

    public function down(): void
    {
        Schema::connection('central')->dropIfExists('agency_invoices');
    }
};
