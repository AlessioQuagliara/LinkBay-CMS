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
        Schema::connection('central')->create('agency_subscriptions', function (Blueprint $table) {
            $table->id();
            $table->unsignedBigInteger('agency_id')->unique();
            $table->unsignedBigInteger('plan_id')->nullable();
            $table->string('stripe_subscription_id')->nullable()->unique();
            $table->string('stripe_customer_id')->nullable();
            $table->string('status', 20)->default('active');
            // status: trialing | active | past_due | cancelled | paused
            $table->string('billing_type', 20)->default('monthly');
            // billing_type: monthly | yearly | lifetime
            $table->timestamp('current_period_start')->nullable();
            $table->timestamp('current_period_end')->nullable();   // null for lifetime
            $table->timestamp('trial_ends_at')->nullable();
            $table->timestamp('cancelled_at')->nullable();
            $table->timestamps();

            $table->foreign('agency_id')->references('id')->on('agencies')->onDelete('cascade');
            $table->foreign('plan_id')->references('id')->on('plans')->onDelete('set null');
        });
    }

    public function down(): void
    {
        Schema::connection('central')->dropIfExists('agency_subscriptions');
    }
};
