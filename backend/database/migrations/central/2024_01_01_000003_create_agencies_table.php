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
        Schema::connection('central')->create('agencies', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('slug')->unique();
            $table->string('domain')->nullable()->unique();
            $table->string('logo_url')->nullable();
            $table->string('favicon_url')->nullable();
            $table->string('primary_color', 7)->default('#f59e0b');
            $table->string('brand_name');
            $table->string('support_email')->nullable();
            $table->string('support_url')->nullable();
            $table->boolean('hide_linkbay_branding')->default(false);
            $table->unsignedBigInteger('owner_user_id')->nullable();
            $table->unsignedBigInteger('plan_id')->nullable();
            $table->string('status')->default('active');
            $table->timestamps();

            $table->foreign('plan_id')->references('id')->on('plans')->onDelete('set null');
        });

        Schema::connection('central')->table('tenants', function (Blueprint $table) {
            $table->unsignedBigInteger('agency_id')->nullable()->after('plan_id');
            $table->foreign('agency_id')->references('id')->on('agencies')->onDelete('set null');
        });
    }

    public function down(): void
    {
        Schema::connection('central')->table('tenants', function (Blueprint $table) {
            $table->dropForeign(['agency_id']);
            $table->dropColumn('agency_id');
        });
        Schema::connection('central')->dropIfExists('agencies');
    }
};
