<?php

declare(strict_types=1);

namespace App\Services\Tenant;

use App\Models\Tenant\BrandSetting;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Storage;

class BrandService
{
    public function getCurrent(): BrandSetting
    {
        return BrandSetting::current();
    }

    public function update(array $data): BrandSetting
    {
        $brand = BrandSetting::current();
        $brand->update($data);

        return $brand->fresh();
    }

    public function uploadLogo(UploadedFile $file): BrandSetting
    {
        $brand = BrandSetting::current();
        $path = $this->storeFile($file, 'brand/logo');

        if ($brand->logo_url) {
            $this->deleteByUrl($brand->logo_url);
        }

        $brand->update(['logo_url' => Storage::disk('public')->url($path)]);

        return $brand->fresh();
    }

    public function uploadFavicon(UploadedFile $file): BrandSetting
    {
        $brand = BrandSetting::current();
        $path = $this->storeFile($file, 'brand/favicon');

        if ($brand->favicon_url) {
            $this->deleteByUrl($brand->favicon_url);
        }

        $brand->update(['favicon_url' => Storage::disk('public')->url($path)]);

        return $brand->fresh();
    }

    public function generateCssVariables(BrandSetting $brand): string
    {
        $vars = [];

        if ($brand->primary_color) {
            $vars[] = "--color-primary: {$brand->primary_color}";
        }
        if ($brand->secondary_color) {
            $vars[] = "--color-secondary: {$brand->secondary_color}";
        }
        if ($brand->accent_color) {
            $vars[] = "--color-accent: {$brand->accent_color}";
        }
        if ($brand->font_heading) {
            $vars[] = "--font-heading: '{$brand->font_heading}', sans-serif";
        }
        if ($brand->font_body) {
            $vars[] = "--font-body: '{$brand->font_body}', sans-serif";
        }

        if (empty($vars)) {
            return '';
        }

        $declarations = implode(";\n    ", $vars);

        $css = ":root {\n    {$declarations};\n}";

        if ($brand->custom_css) {
            $css .= "\n\n".$brand->custom_css;
        }

        return $css;
    }

    private function storeFile(UploadedFile $file, string $dir): string
    {
        return $file->store($dir, 'public');
    }

    private function deleteByUrl(string $url): void
    {
        $base = rtrim(Storage::disk('public')->url(''), '/');
        $path = ltrim(str_replace($base, '', $url), '/');

        if ($path && Storage::disk('public')->exists($path)) {
            Storage::disk('public')->delete($path);
        }
    }
}
