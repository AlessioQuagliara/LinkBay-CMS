<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('brand_settings', function (Blueprint $table) {
            $table->id();
            $table->string('tenant_id')->unique();
            $table->string('logo_url')->nullable();
            $table->string('favicon_url')->nullable();
            $table->string('primary_color', 20)->default('#000000');
            $table->string('secondary_color', 20)->nullable();
            $table->string('accent_color', 20)->nullable();
            $table->string('font_heading')->nullable();
            $table->string('font_body')->nullable();
            $table->string('store_name')->default('');
            $table->text('store_description')->nullable();
            $table->string('contact_email')->nullable();
            $table->string('contact_phone')->nullable();
            $table->json('social_links')->nullable();
            $table->longText('custom_css')->nullable();
            $table->longText('custom_js')->nullable();
            $table->string('meta_pixel_id')->nullable();
            $table->string('google_analytics_id')->nullable();
            $table->boolean('cookie_banner_enabled')->default(true);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('brand_settings');
    }
};
