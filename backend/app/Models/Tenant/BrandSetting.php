<?php

declare(strict_types=1);

namespace App\Models\Tenant;

use Illuminate\Database\Eloquent\Model;

class BrandSetting extends Model
{
    protected $table = 'brand_settings';

    protected $fillable = [
        'tenant_id',
        'logo_url',
        'favicon_url',
        'primary_color',
        'secondary_color',
        'accent_color',
        'font_heading',
        'font_body',
        'store_name',
        'store_description',
        'contact_email',
        'contact_phone',
        'social_links',
        'custom_css',
        'custom_js',
        'meta_pixel_id',
        'google_analytics_id',
        'cookie_banner_enabled',
    ];

    protected $casts = [
        'social_links' => 'array',
        'cookie_banner_enabled' => 'boolean',
    ];

    public static function current(): static
    {
        $tenantId = static::resolveTenantId();

        return static::firstOrCreate(
            ['tenant_id' => $tenantId],
            ['store_name' => '', 'primary_color' => '#000000', 'cookie_banner_enabled' => true]
        );
    }

    private static function resolveTenantId(): string
    {
        try {
            if (function_exists('tenancy') && tenancy()->initialized) {
                return (string) tenant()->id;
            }
        } catch (\Throwable) {
        }

        return 'default';
    }
}
