<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tenant;

use App\Http\Controllers\Controller;
use App\Models\Tenant\Category;
use App\Models\Tenant\Collection;
use App\Models\Tenant\Page;
use App\Models\Tenant\Product;
use Illuminate\Http\Response;

class SitemapController extends Controller
{
    private const PRODUCT_SITEMAP_THRESHOLD = 1000;

    public function index(): Response
    {
        $baseUrl = request()->getSchemeAndHttpHost();
        $productCount = Product::where('is_active', true)->count();

        if ($productCount > self::PRODUCT_SITEMAP_THRESHOLD) {
            return $this->sitemapIndex($baseUrl);
        }

        return $this->fullSitemap($baseUrl);
    }

    public function robots(): Response
    {
        $sitemapUrl = request()->getSchemeAndHttpHost().'/sitemap.xml';

        $content = implode("\n", [
            'User-agent: *',
            'Allow: /',
            "Sitemap: {$sitemapUrl}",
        ]);

        return response($content, 200, [
            'Content-Type' => 'text/plain; charset=UTF-8',
        ]);
    }

    private function fullSitemap(string $baseUrl): Response
    {
        $urls = [];

        // Homepage
        $urls[] = $this->url($baseUrl.'/', now(), 'daily', '1.0');

        // CMS pages
        Page::where('is_published', true)
            ->where('visibility', 'public')
            ->whereNotNull('published_at')
            ->orderBy('updated_at', 'desc')
            ->each(function (Page $page) use ($baseUrl, &$urls) {
                $urls[] = $this->url(
                    $baseUrl.'/'.$page->slug,
                    $page->updated_at,
                    'weekly',
                    $page->is_homepage ? '0.9' : '0.7',
                );
            });

        // Active products
        Product::where('is_active', true)
            ->orderBy('updated_at', 'desc')
            ->each(function (Product $product) use ($baseUrl, &$urls) {
                $urls[] = $this->url(
                    $baseUrl.'/products/'.$product->slug,
                    $product->updated_at,
                    'weekly',
                    '0.8',
                );
            });

        // Active categories
        Category::where('is_active', true)
            ->orderBy('sort_order')
            ->each(function (Category $category) use ($baseUrl, &$urls) {
                $urls[] = $this->url(
                    $baseUrl.'/shop/'.$category->slug,
                    $category->updated_at,
                    'weekly',
                    '0.6',
                );
            });

        // Active collections
        Collection::where('is_active', true)
            ->orderBy('sort_order')
            ->each(function (Collection $collection) use ($baseUrl, &$urls) {
                $urls[] = $this->url(
                    $baseUrl.'/collections/'.$collection->slug,
                    $collection->updated_at,
                    'weekly',
                    '0.6',
                );
            });

        $xml = $this->buildUrlset($urls);

        return response($xml, 200, [
            'Content-Type' => 'application/xml; charset=UTF-8',
            'Cache-Control' => 'public, max-age=3600',
        ]);
    }

    private function sitemapIndex(string $baseUrl): Response
    {
        $sitemaps = [
            $baseUrl.'/sitemap.xml?section=pages',
            $baseUrl.'/sitemap.xml?section=products',
            $baseUrl.'/sitemap.xml?section=collections',
        ];

        $xml = '<?xml version="1.0" encoding="UTF-8"?>'."\n";
        $xml .= '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'."\n";

        foreach ($sitemaps as $sitemap) {
            $xml .= "  <sitemap>\n";
            $xml .= '    <loc>'.htmlspecialchars($sitemap).'</loc>'."\n";
            $xml .= '    <lastmod>'.now()->toAtomString().'</lastmod>'."\n";
            $xml .= "  </sitemap>\n";
        }

        $xml .= '</sitemapindex>';

        return response($xml, 200, [
            'Content-Type' => 'application/xml; charset=UTF-8',
            'Cache-Control' => 'public, max-age=3600',
        ]);
    }

    private function url(string $loc, mixed $lastmod, string $changefreq, string $priority): string
    {
        $lastmodStr = $lastmod instanceof \DateTimeInterface
            ? $lastmod->format('Y-m-d')
            : now()->format('Y-m-d');

        return implode("\n", [
            '  <url>',
            '    <loc>'.htmlspecialchars($loc).'</loc>',
            "    <lastmod>{$lastmodStr}</lastmod>",
            "    <changefreq>{$changefreq}</changefreq>",
            "    <priority>{$priority}</priority>",
            '  </url>',
        ]);
    }

    private function buildUrlset(array $urls): string
    {
        $xml = '<?xml version="1.0" encoding="UTF-8"?>'."\n";
        $xml .= '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'."\n";
        $xml .= implode("\n", $urls)."\n";
        $xml .= '</urlset>';

        return $xml;
    }
}
