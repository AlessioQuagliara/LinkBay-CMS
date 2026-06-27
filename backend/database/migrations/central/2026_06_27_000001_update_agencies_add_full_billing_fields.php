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
        Schema::connection('central')->table('agencies', function (Blueprint $table) {
            $table->string('stripe_subscription_id')->nullable()->after('stripe_customer_id');
            $table->string('stripe_status', 20)->nullable()->after('stripe_subscription_id');
            // stripe_status: incomplete | active | past_due | canceled | paused
            $table->timestamp('trial_ends_at')->nullable()->after('stripe_status');
            $table->timestamp('subscription_ends_at')->nullable()->after('trial_ends_at');
            $table->string('payment_method_last4', 4)->nullable()->after('subscription_ends_at');
            $table->string('payment_method_brand', 20)->nullable()->after('payment_method_last4');
            $table->string('billing_email')->nullable()->after('payment_method_brand');
            $table->string('billing_name')->nullable()->after('billing_email');
            $table->string('vat_number', 50)->nullable()->after('billing_name');
            $table->json('billing_address')->nullable()->after('vat_number');

            $table->index('stripe_customer_id');
            $table->index('stripe_subscription_id');
        });
    }

    public function down(): void
    {
        Schema::connection('central')->table('agencies', function (Blueprint $table) {
            $table->dropIndex(['stripe_customer_id']);
            $table->dropIndex(['stripe_subscription_id']);
            $table->dropColumn([
                'stripe_subscription_id',
                'stripe_status',
                'trial_ends_at',
                'subscription_ends_at',
                'payment_method_last4',
                'payment_method_brand',
                'billing_email',
                'billing_name',
                'vat_number',
                'billing_address',
            ]);
        });
    }
};
