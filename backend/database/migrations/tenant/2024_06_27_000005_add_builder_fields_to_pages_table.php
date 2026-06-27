<?php

declare(strict_types=1);

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('pages', function (Blueprint $table) {
            $table->string('seo_title')->nullable()->after('meta_description');
            $table->string('seo_description')->nullable()->after('seo_title');
            $table->string('og_image_url')->nullable()->after('seo_description');
            $table->json('blocks')->nullable()->after('content');
            $table->boolean('is_homepage')->default(false)->after('is_published');
            $table->string('template')->nullable()->after('is_homepage');
            $table->timestamp('published_at')->nullable()->after('template');
            $table->string('visibility')->default('public')->after('published_at');
            $table->string('page_password')->nullable()->after('visibility');
        });
    }

    public function down(): void
    {
        Schema::table('pages', function (Blueprint $table) {
            $table->dropColumn([
                'seo_title',
                'seo_description',
                'og_image_url',
                'blocks',
                'is_homepage',
                'template',
                'published_at',
                'visibility',
                'page_password',
            ]);
        });
    }
};
