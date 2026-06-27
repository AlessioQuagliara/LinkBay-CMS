<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tenant\Storefront;

use App\Http\Controllers\Controller;
use App\Models\Tenant\Page;
use App\Services\Tenant\PageBuilderService;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;

class StorePageController extends Controller
{
    public function __construct(private readonly PageBuilderService $builder) {}

    public function show(Request $request, string $slug): JsonResponse
    {
        $page = Page::where('slug', $slug)
            ->where('is_published', true)
            ->where('visibility', 'public')
            ->firstOrFail();

        $locale = $request->query('locale');

        return response()->json([
            'data' => [
                'id' => $page->id,
                'slug' => $page->slug,
                'title' => $page->title,
                'is_homepage' => $page->is_homepage,
                'template' => $page->template,
                'visibility' => $page->visibility,
                'published_at' => $page->published_at?->toIso8601String(),
                'seo' => [
                    'title' => $page->seo_title ?? $page->meta_title ?? $page->title,
                    'description' => $page->seo_description ?? $page->meta_description,
                    'og_image_url' => $page->og_image_url,
                ],
                'blocks' => $page->blocks ?? [],
                'rendered_html' => $this->builder->renderPage($page, $locale),
            ],
        ]);
    }
}
