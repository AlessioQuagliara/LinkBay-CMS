<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('orders', function (Blueprint $table) {
            $table->string('stripe_payment_intent_id')->nullable()->after('payment_status');
            $table->string('stripe_charge_id')->nullable()->after('stripe_payment_intent_id');
            $table->string('payment_method_type', 30)->nullable()->after('stripe_charge_id');
            $table->decimal('refunded_amount', 12, 2)->default(0)->after('payment_method_type');
            $table->string('refund_reason')->nullable()->after('refunded_amount');
            $table->timestamp('captured_at')->nullable()->after('refund_reason');
            $table->timestamp('refunded_at')->nullable()->after('captured_at');

            $table->index('stripe_payment_intent_id');
        });
    }

    public function down(): void
    {
        Schema::table('orders', function (Blueprint $table) {
            $table->dropIndex(['stripe_payment_intent_id']);
            $table->dropColumn([
                'stripe_payment_intent_id',
                'stripe_charge_id',
                'payment_method_type',
                'refunded_amount',
                'refund_reason',
                'captured_at',
                'refunded_at',
            ]);
        });
    }
};
