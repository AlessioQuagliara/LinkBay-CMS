<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Central\Agency;
use App\Models\Central\LayoutAssignment;
use App\Models\Central\LayoutTemplate;
use App\Models\Central\Tenant;
use App\Models\Central\ThemeAssignment;
use App\Models\Central\ThemePreset;
use App\Models\Central\UsageEvent;
use App\Plugins\PluginRegistry;
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
 *  - Premium enforcement: blocks/themes requiring a feature the agency lacks are excluded
 *    or replaced with a safe fallback (theme only).
 *
 * Usage (storefront controller / Next.js API proxy):
 *   $blocks = app(LayoutRendererService::class)->render($template->blocks ?? []);
 *   // $blocks is a Collection<int, array{type: string, data: array}>
 *   // Pass to view or serialize as JSON for the frontend.
 */
class LayoutRendererService
{
    public function __construct(
        private readonly UsageEventService $usage,
        private readonly FeatureAccessService $access,
    ) {}

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
     * Applies premium enforcement: blocks whose featureCode the agency cannot access are
     * silently excluded; a premium theme the agency cannot access falls back to defaults.
     * The payload is always structurally valid — no hard failures.
     *
     * Returns null if no layout template is assigned to the requested page slot.
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

        $agency = Tenant::with('agency.plan')->find($tenantId)?->agency;

        $blocks = $this->renderTemplate($layoutAssignment->layoutTemplate);
        $blocks = $this->enforcePremiumBlocks($blocks, $agency, $tenantId);

        $themeAssignment = ThemeAssignment::where('tenant_id', $tenantId)
            ->with('themePreset')
            ->first();

        $themeConfig = $this->resolveThemeConfig($themeAssignment?->themePreset, $agency);

        $this->trackStorefrontRendered($tenantId, $pageKey, $agency, $themeAssignment?->themePreset);

        return [
            'theme' => $themeConfig,
            'blocks' => $blocks->toArray(),
        ];
    }

    // ── Private: premium enforcement ──────────────────────────────────────────

    /**
     * Exclude any block whose featureCode the agency cannot access.
     * Free blocks (featureCode = null) are always kept.
     * If agency is null, all premium blocks are excluded (fail-safe).
     *
     * @param  Collection<int, array{type: string, data: array<string, mixed>}>  $blocks
     * @return Collection<int, array{type: string, data: array<string, mixed>}>
     */
    private function enforcePremiumBlocks(Collection $blocks, ?Agency $agency, string $tenantId): Collection
    {
        $registry = app(PluginRegistry::class);

        return $blocks->filter(function (array $block) use ($registry, $agency, $tenantId): bool {
            $def = $registry->getBlock($block['type'] ?? '');

            if ($def === null || $def->featureCode === null) {
                return true; // free block: always keep
            }

            if ($agency === null || ! $this->access->canUseFeature($agency, $def->featureCode)) {
                return false;
            }

            $this->usage->track(
                eventType: UsageEvent::EVENT_PREMIUM_BLOCK_RENDERED,
                tenantId: $tenantId,
                agencyId: $agency->id,
                meta: ['block_type' => $block['type'], 'feature_code' => $def->featureCode],
            );

            return true;
        })->values();
    }

    /**
     * Resolve the theme config to serve, applying premium enforcement.
     *
     * Rules:
     *  - No preset assigned → defaults
     *  - Fork preset → resolve parent base + agency overrides (with premium check on parent)
     *  - Custom preset (is_system = false, no parent) → always allowed (agency-created config)
     *  - System preset with no featureCode → always allowed (free theme)
     *  - System preset with featureCode the agency can access → use preset config
     *  - System preset with featureCode the agency cannot access → defaults (fail-safe)
     *
     * @return array<string, mixed>
     */
    private function resolveThemeConfig(?ThemePreset $preset, ?Agency $agency): array
    {
        if ($preset === null) {
            return ThemeConfigSchema::defaults();
        }

        // Fork: agency-owned preset that inherits from a parent system theme
        if ($preset->isFork()) {
            $parentDef = app(PluginRegistry::class)->getTheme($preset->parent_theme_slug);

            // If parent is premium, the fork requires the same entitlement
            if ($parentDef?->featureCode !== null) {
                if ($agency === null || ! $this->access->canUseFeature($agency, $parentDef->featureCode)) {
                    return ThemeConfigSchema::defaults(); // fail-safe: no scaping premium via fork
                }
            }

            return $preset->resolvedConfig();
        }

        if (! $preset->isSystem()) {
            return $preset->normalizedConfig();
        }

        // System preset — look up its ThemeDefinition for featureCode
        $def = app(PluginRegistry::class)->getTheme($preset->slug);

        if ($def === null || $def->featureCode === null) {
            return $preset->normalizedConfig();
        }

        // Premium system theme — verify access
        if ($agency !== null && $this->access->canUseFeature($agency, $def->featureCode)) {
            return $preset->normalizedConfig();
        }

        return ThemeConfigSchema::defaults();
    }

    // ── Private: usage tracking ───────────────────────────────────────────────

    private function trackStorefrontRendered(
        string $tenantId,
        string $pageKey,
        ?Agency $agency,
        ?ThemePreset $preset,
    ): void {
        $this->usage->track(
            eventType: UsageEvent::EVENT_STOREFRONT_RENDERED,
            tenantId: $tenantId,
            agencyId: $agency?->id,
            meta: ['page_key' => $pageKey],
        );

        if ($preset === null) {
            return;
        }

        // Track premium theme rendering (system preset or fork of a premium parent)
        $themeSlugForDef = $preset->isFork() ? $preset->parent_theme_slug : $preset->slug;
        $def = $themeSlugForDef ? app(PluginRegistry::class)->getTheme($themeSlugForDef) : null;

        if ($def?->featureCode !== null
            && $agency !== null
            && $this->access->canUseFeature($agency, $def->featureCode)
        ) {
            $this->usage->track(
                eventType: UsageEvent::EVENT_THEME_RENDERED,
                tenantId: $tenantId,
                agencyId: $agency->id,
                meta: ['theme_slug' => $preset->slug, 'feature_code' => $def->featureCode],
            );
        }
    }

    // ── Private: sanitization ─────────────────────────────────────────────────

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
