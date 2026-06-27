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
        Schema::connection('central')->table('plans', function (Blueprint $table) {
            $table->string('stripe_product_id')->nullable()->after('stripe_price_id');
            $table->string('stripe_price_id_monthly')->nullable()->after('stripe_product_id');
            $table->string('stripe_price_id_yearly')->nullable()->after('stripe_price_id_monthly');
            $table->unsignedInteger('trial_days')->default(0)->after('stripe_price_id_yearly');
            $table->unsignedInteger('max_stores')->nullable()->after('trial_days');
            $table->unsignedInteger('max_members')->nullable()->after('max_stores');
            $table->unsignedInteger('storage_gb')->nullable()->after('max_members');
        });
    }

    public function down(): void
    {
        Schema::connection('central')->table('plans', function (Blueprint $table) {
            $table->dropColumn([
                'stripe_product_id',
                'stripe_price_id_monthly',
                'stripe_price_id_yearly',
                'trial_days',
                'max_stores',
                'max_members',
                'storage_gb',
            ]);
        });
    }
};
