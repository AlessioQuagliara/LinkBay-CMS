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
        Schema::connection('central')->table('agency_client_contacts', function (Blueprint $table) {
            $table->string('invite_token', 64)->nullable()->unique()->after('can_access_tenant');
            $table->string('invite_tenant_id')->nullable()->after('invite_token');
            $table->timestamp('invite_expires_at')->nullable()->after('invite_tenant_id');
        });
    }

    public function down(): void
    {
        Schema::connection('central')->table('agency_client_contacts', function (Blueprint $table) {
            $table->dropColumn(['invite_token', 'invite_tenant_id', 'invite_expires_at']);
        });
    }
};
