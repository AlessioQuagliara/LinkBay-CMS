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
        Schema::connection('central')->create('commission_records', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('agency_id');
            $table->string('tenant_id')->nullable();
            $table->unsignedBigInteger('platform_fee_rule_id');
            $table->string('stripe_payment_intent_id')->nullable()->index();
            $table->string('stripe_charge_id')->nullable()->index();
            $table->integer('gross_amount_cents');
            $table->decimal('fee_pct', 5, 4);          // snapshot al momento della transazione
            $table->integer('fee_amount_cents');
            $table->integer('net_to_agency_cents');
            $table->char('currency', 3)->default('eur');
            $table->string('status', 20)->default('pending');
            // status: pending | settled | refunded | disputed
            $table->timestamp('settled_at')->nullable();
            $table->integer('refund_amount_cents')->default(0);
            $table->jsonb('metadata')->nullable();
            $table->timestamp('created_at')->useCurrent();
            // NO updated_at — append-only; refund/dispute creano record separati

            $table->foreign('agency_id')->references('id')->on('agencies')->onDelete('cascade');
            $table->foreign('platform_fee_rule_id')->references('id')->on('platform_fee_rules')->onDelete('restrict');

            $table->index(['agency_id', 'created_at']);
            $table->index(['agency_id', 'status']);
        });
    }

    public function down(): void
    {
        Schema::connection('central')->dropIfExists('commission_records');
    }
};
