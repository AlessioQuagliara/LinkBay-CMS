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
        Schema::connection('central')->create('ai_credit_packages', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->integer('credits');
            $table->integer('price_cents');
            $table->string('stripe_price_id')->nullable();
            $table->boolean('is_active')->default(true);
            $table->integer('sort_order')->default(0);
            $table->timestamps();
        });

        Schema::connection('central')->create('ai_credit_ledger', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('agency_id');
            $table->string('tenant_id')->nullable();
            $table->integer('amount');
            $table->integer('balance_after')->default(0);
            $table->string('type');
            $table->string('description');
            $table->string('stripe_payment_intent_id')->nullable();
            $table->json('metadata')->nullable();
            $table->timestamp('created_at')->useCurrent();

            $table->foreign('agency_id')->references('id')->on('agencies')->onDelete('cascade');
            $table->index(['agency_id', 'created_at']);
        });
    }

    public function down(): void
    {
        Schema::connection('central')->dropIfExists('ai_credit_ledger');
        Schema::connection('central')->dropIfExists('ai_credit_packages');
    }
};
