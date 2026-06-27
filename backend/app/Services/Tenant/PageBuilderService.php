<?php

declare(strict_types=1);

namespace App\Services\Tenant;

use App\Models\Tenant\Page;
use Illuminate\Support\Str;

class PageBuilderService
{
    private const VALID_TYPES = ['hero', 'text', 'products', 'banner', 'html', 'spacer'];

    public function getBlocks(Page $page): array
    {
        return $page->blocks ?? [];
    }

    public function saveBlocks(Page $page, array $blocks): Page
    {
        $blocks = array_map(fn (array $b) => $this->normaliseBlock($b), $blocks);
        $page->update(['blocks' => array_values($blocks)]);

        return $page->fresh();
    }

    public function addBlock(Page $page, array $block): Page
    {
        $blocks = $this->getBlocks($page);
        $blocks[] = $this->normaliseBlock($block);

        return $this->saveBlocks($page, $blocks);
    }

    public function reorderBlocks(Page $page, array $orderedIds): Page
    {
        $blocks = collect($this->getBlocks($page))->keyBy('id');
        $reordered = array_map(fn (string $id) => $blocks->get($id), $orderedIds);

        return $this->saveBlocks($page, array_filter($reordered));
    }

    public function removeBlock(Page $page, string $blockId): Page
    {
        $blocks = array_filter(
            $this->getBlocks($page),
            fn (array $b) => $b['id'] !== $blockId
        );

        return $this->saveBlocks($page, $blocks);
    }

    public function renderPage(Page $page, ?string $locale = null): string
    {
        $blocks = $this->getBlocks($page);
        $html = '';

        foreach ($blocks as $block) {
            if (! ($block['visible'] ?? true)) {
                continue;
            }
            $html .= $this->renderBlock($block, $locale);
        }

        return $html;
    }

    private function normaliseBlock(array $block): array
    {
        return [
            'id' => $block['id'] ?? (string) Str::uuid(),
            'type' => in_array($block['type'] ?? '', self::VALID_TYPES, true) ? $block['type'] : 'text',
            'data' => $block['data'] ?? [],
            'visible' => (bool) ($block['visible'] ?? true),
        ];
    }

    private function renderBlock(array $block, ?string $locale): string
    {
        $type = $block['type'];
        $data = $block['data'] ?? [];

        return match ($type) {
            'hero' => $this->renderHero($data, $locale),
            'text' => $this->renderText($data, $locale),
            'banner' => $this->renderBanner($data, $locale),
            'html' => $this->renderHtml($data),
            'spacer' => $this->renderSpacer($data),
            'products' => '',  // rendered client-side by storefront
            default => '',
        };
    }

    private function renderHero(array $data, ?string $locale): string
    {
        $title = e($data['title'] ?? '');
        $subtitle = e($data['subtitle'] ?? '');
        $bg = e($data['background_url'] ?? '');
        $cta = e($data['cta_text'] ?? '');
        $ctaUrl = e($data['cta_url'] ?? '#');

        return <<<HTML
        <section class="lb-hero" style="background-image:url('{$bg}')">
          <h1>{$title}</h1>
          <p>{$subtitle}</p>
          {$this->renderCta($cta, $ctaUrl)}
        </section>
        HTML;
    }

    private function renderText(array $data, ?string $locale): string
    {
        $body = $data['body'] ?? '';

        return "<div class=\"lb-text\">{$body}</div>";
    }

    private function renderBanner(array $data, ?string $locale): string
    {
        $text = e($data['text'] ?? '');
        $bg = e($data['background_color'] ?? '#f5f5f5');
        $cta = e($data['cta_text'] ?? '');
        $ctaUrl = e($data['cta_url'] ?? '#');

        return <<<HTML
        <section class="lb-banner" style="background:{$bg}">
          <p>{$text}</p>
          {$this->renderCta($cta, $ctaUrl)}
        </section>
        HTML;
    }

    private function renderHtml(array $data): string
    {
        return $data['html'] ?? '';
    }

    private function renderSpacer(array $data): string
    {
        $height = (int) ($data['height'] ?? 40);

        return "<div class=\"lb-spacer\" style=\"height:{$height}px\"></div>";
    }

    private function renderCta(string $text, string $url): string
    {
        if (! $text) {
            return '';
        }

        return "<a class=\"lb-cta\" href=\"{$url}\">{$text}</a>";
    }
}
