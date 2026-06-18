<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Central\LayoutAssignment;
use App\Models\Central\LayoutTemplate;
use App\Models\Central\ThemeAssignment;
use Illuminate\Support\Collection;
use Illuminate\Support\HtmlString;
use Illuminate\Support\Str;

/**
 * Transforms a LayoutTemplate's raw blocks into a safe, renderable data structure.
 *
 * Responsibilities:
 *  - Whitelist: silently drops any block type not in LayoutBlockSchema::knownTypes()
 *  - rich_text.content: Markdown → HTML via Str::markdown() with HTML stripped from input
 *  - All other string fields: plain text, no HTML injection possible
 *
 * Usage (storefront controller / Next.js API proxy):
 *   $blocks = app(LayoutRendererService::class)->render($template->blocks ?? []);
 *   // $blocks is a Collection<int, array{type: string, data: array}>
 *   // Pass to view or serialize as JSON for the frontend.
 */
class LayoutRendererService
{
    /**
     * @param  array<int, array{type: string, data: array<string, mixed>}>  $blocks
     * @return Collection<int, array{type: string, data: array<string, mixed>}>
     */
    public function render(array $blocks): Collection
    {
        $known = LayoutBlockSchema::knownTypes();

        return collect($blocks)
            ->filter(fn (array $block) => in_array($block['type'] ?? '', $known, true))
            ->map(fn (array $block) => [
                'type' => $block['type'],
                'data' => $this->sanitize($block['type'], $block['data'] ?? []),
            ])
            ->values();
    }

    /**
     * Convenience wrapper: resolves template and returns rendered blocks.
     * Returns empty collection if the template is not published.
     *
     * @return Collection<int, array{type: string, data: array<string, mixed>}>
     */
    public function renderTemplate(LayoutTemplate $template): Collection
    {
        if (! $template->isPublished()) {
            return collect();
        }

        return $this->render($template->blocks ?? []);
    }

    /**
     * Combine layout + theme for a given store page into a single storefront payload.
     *
     * Returns null if no layout template is assigned to the requested page slot.
     * Falls back to ThemeConfigSchema::defaults() when no theme is assigned to the tenant.
     *
     * Example payload:
     * [
     *   'theme'  => ['palette' => [...], 'typography' => [...], 'radius' => 'md', ...],
     *   'blocks' => [['type' => 'hero', 'data' => [...]], ...],
     * ]
     *
     * @return array{theme: array<string, mixed>, blocks: array<int, array{type: string, data: array<string, mixed>}>}|null
     */
    public function renderStorefront(string $tenantId, string $pageKey): ?array
    {
        $layoutAssignment = LayoutAssignment::where('tenant_id', $tenantId)
            ->where('page_key', $pageKey)
            ->with('layoutTemplate')
            ->first();

        if (! $layoutAssignment || ! $layoutAssignment->layoutTemplate) {
            return null;
        }

        $blocks = $this->renderTemplate($layoutAssignment->layoutTemplate);

        $themeAssignment = ThemeAssignment::where('tenant_id', $tenantId)
            ->with('themePreset')
            ->first();

        $themeConfig = $themeAssignment?->themePreset
            ? ThemeConfigSchema::normalize($themeAssignment->themePreset->config ?? [])
            : ThemeConfigSchema::defaults();

        return [
            'theme' => $themeConfig,
            'blocks' => $blocks->toArray(),
        ];
    }

    /**
     * @param  array<string, mixed>  $data
     * @return array<string, mixed>
     */
    private function sanitize(string $type, array $data): array
    {
        if ($type === 'rich_text' && isset($data['content'])) {
            // Remove dangerous tags with their content first (script/style/etc),
            // then strip remaining tags. This ensures tag content (e.g. JS code
            // inside <script>) never makes it into the rendered Markdown.
            $stripped = preg_replace('/<(script|style|iframe|object|embed|form)\b[^>]*>.*?<\/\1>/is', '', (string) $data['content']) ?? '';
            $safeMarkdown = strip_tags($stripped);
            $data['content_html'] = new HtmlString(Str::markdown($safeMarkdown));
        }

        return $data;
    }
}
