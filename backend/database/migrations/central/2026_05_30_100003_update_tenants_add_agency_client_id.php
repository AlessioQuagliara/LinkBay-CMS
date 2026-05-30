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
        Schema::connection('central')->table('tenants', function (Blueprint $table) {
            $table->unsignedBigInteger('agency_client_id')->nullable()->after('agency_id');
            $table->foreign('agency_client_id')
                ->references('id')->on('agency_clients')->onDelete('set null');
            $table->index('agency_client_id');
        });
    }

    public function down(): void
    {
        Schema::connection('central')->table('tenants', function (Blueprint $table) {
            $table->dropForeign(['agency_client_id']);
            $table->dropIndex(['agency_client_id']);
            $table->dropColumn('agency_client_id');
        });
    }
};
