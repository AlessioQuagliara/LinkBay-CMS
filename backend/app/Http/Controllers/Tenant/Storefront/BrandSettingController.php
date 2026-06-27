<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tenant\Storefront;

use App\Http\Controllers\Controller;
use App\Models\Tenant\BrandSetting;
use App\Services\Tenant\BrandService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Response;

class BrandSettingController extends Controller
{
    public function __construct(private readonly BrandService $brandService) {}

    public function show(): JsonResponse
    {
        $brand = BrandSetting::current();

        return response()->json([
            'data' => [
                'store_name' => $brand->store_name,
                'store_description' => $brand->store_description,
                'logo_url' => $brand->logo_url,
                'favicon_url' => $brand->favicon_url,
                'primary_color' => $brand->primary_color,
                'secondary_color' => $brand->secondary_color,
                'accent_color' => $brand->accent_color,
                'font_heading' => $brand->font_heading,
                'font_body' => $brand->font_body,
                'contact_email' => $brand->contact_email,
                'contact_phone' => $brand->contact_phone,
                'social_links' => $brand->social_links ?? [],
                'meta_pixel_id' => $brand->meta_pixel_id,
                'google_analytics_id' => $brand->google_analytics_id,
                'cookie_banner_enabled' => $brand->cookie_banner_enabled,
            ],
        ]);
    }

    public function css(): Response
    {
        $brand = BrandSetting::current();
        $css = $this->brandService->generateCssVariables($brand);

        return response($css, 200, [
            'Content-Type' => 'text/css; charset=UTF-8',
            'Cache-Control' => 'public, max-age=3600',
        ]);
    }
}
