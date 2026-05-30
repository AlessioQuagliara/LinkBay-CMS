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
            $table->string('stripe_customer_id')->nullable()->after('stripe_connect_onboarded');
            $table->string('terms_accepted_version')->nullable()->after('stripe_customer_id');
            $table->integer('max_stores_override')->nullable()->after('terms_accepted_version');
        });
    }

    public function down(): void
    {
        Schema::connection('central')->table('agencies', function (Blueprint $table) {
            $table->dropColumn(['stripe_customer_id', 'terms_accepted_version', 'max_stores_override']);
        });
    }
};
