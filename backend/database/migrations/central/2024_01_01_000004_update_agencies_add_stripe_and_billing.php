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
            $table->string('custom_domain')->nullable()->unique()->after('slug');
            $table->string('stripe_connect_account_id')->nullable()->after('support_url');
            $table->boolean('stripe_connect_onboarded')->default(false)->after('stripe_connect_account_id');
            $table->string('billing_type')->default('monthly')->after('plan_id');
            $table->string('ltdcode')->nullable()->after('billing_type');
        });

        // Rename domain to match new custom_domain convention if needed
        // domain column already exists from migration 003, custom_domain is new
    }

    public function down(): void
    {
        Schema::connection('central')->table('agencies', function (Blueprint $table) {
            $table->dropColumn([
                'custom_domain',
                'stripe_connect_account_id',
                'stripe_connect_onboarded',
                'billing_type',
                'ltdcode',
            ]);
        });
    }
};
