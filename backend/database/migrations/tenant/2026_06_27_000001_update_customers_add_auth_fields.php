<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('customers', function (Blueprint $table) {
            $table->string('password')->nullable()->after('email');
            $table->string('status')->default('active')->after('password');
            $table->timestamp('email_verified_at')->nullable()->after('status');
            $table->rememberToken()->after('email_verified_at');
            $table->boolean('accepts_marketing')->default(false)->after('remember_token');
            $table->timestamp('last_login_at')->nullable()->after('accepts_marketing');
            $table->unsignedBigInteger('default_shipping_address_id')->nullable()->after('last_login_at');
            $table->unsignedBigInteger('default_billing_address_id')->nullable()->after('default_shipping_address_id');
        });
    }

    public function down(): void
    {
        Schema::table('customers', function (Blueprint $table) {
            $table->dropColumn([
                'password',
                'status',
                'email_verified_at',
                'remember_token',
                'accepts_marketing',
                'last_login_at',
                'default_shipping_address_id',
                'default_billing_address_id',
            ]);
        });
    }
};
