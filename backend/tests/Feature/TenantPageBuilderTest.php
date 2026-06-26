<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Filament\Tenant\Resources\StorePageResource;
use App\Filament\Tenant\Resources\StorePageResource\Pages\CreateStorePage;
use App\Filament\Tenant\Resources\StorePageResource\Pages\EditStorePage;
use App\Models\Tenant\Page;
use Illuminate\Database\QueryException;
use Tests\TenantTestCase;

/**
 * Covers StorePageResource and Tenant\Page model for the web builder feature.
 *
 * Uses TenantTestCase so only tenant migrations run (pages table, users table).
 *
 * Tests:
 *  1.  Page model can be created with all fillable fields
 *  2.  Page 'content' field is cast to array
 *  3.  Page 'is_published' defaults to true
 *  4.  Page 'sort_order' casts to integer
 *  5.  Page slug must be unique (DB constraint)
 *  6.  Page meta_title and meta_description are nullable
 *  7.  StorePageResource uses Tenant\Page model
 *  8.  StorePageResource navigation group is 'Marketing'
 *  9.  StorePageResource has correct navigation icon
 * 10.  StorePageResource plural label is 'Pagine'
 * 11.  StorePageResource registers List/Create/Edit pages
 * 12.  CreateStorePage references StorePageResource
 * 13.  EditStorePage references StorePageResource
 * 14.  Content JSON array is preserved through model update
 */
class TenantPageBuilderTest extends TenantTestCase
{
    private function makePage(array $overrides = []): Page
    {
        static $n = 0;
        $n++;

        return Page::create(array_merge([
            'title' => 'Test Page '.$n,
            'slug' => 'test-page-'.$n,
            'content' => null,
            'is_published' => true,
            'sort_order' => 0,
        ], $overrides));
    }

    // ── Tenant\Page model ─────────────────────────────────────────────────────

    public function test_page_can_be_created_with_all_fillable_fields(): void
    {
        $page = $this->makePage([
            'title' => 'Chi siamo',
            'slug' => 'chi-siamo',
            'content' => [['type' => 'hero', 'data' => ['heading' => 'Ciao']]],
            'meta_title' => 'Chi siamo | Store',
            'meta_description' => 'La nostra storia',
            'is_published' => true,
            'sort_order' => 1,
        ]);

        $this->assertDatabaseHas('pages', ['slug' => 'chi-siamo', 'title' => 'Chi siamo']);
    }

    public function test_page_content_is_cast_to_array(): void
    {
        $blocks = [['type' => 'hero', 'data' => ['heading' => 'Hello']]];
        $page = $this->makePage(['content' => $blocks]);

        $fresh = Page::find($page->id);
        $this->assertIsArray($fresh->content);
        $this->assertEquals('hero', $fresh->content[0]['type']);
    }

    public function test_page_is_published_defaults_to_true(): void
    {
        $page = Page::create([
            'title' => 'Default Page',
            'slug' => 'default-page',
        ]);

        // DB-level default; read back from DB to verify it was persisted as true
        $this->assertTrue($page->fresh()->is_published);
    }

    public function test_page_sort_order_casts_to_integer(): void
    {
        $page = $this->makePage(['sort_order' => 3]);

        $this->assertSame(3, $page->fresh()->sort_order);
    }

    public function test_page_slug_is_unique(): void
    {
        $this->makePage(['slug' => 'unique-slug']);

        $this->expectException(QueryException::class);

        $this->makePage(['slug' => 'unique-slug']);
    }

    public function test_page_meta_fields_are_nullable(): void
    {
        $page = $this->makePage(['meta_title' => null, 'meta_description' => null]);

        $this->assertNull($page->meta_title);
        $this->assertNull($page->meta_description);
    }

    // ── StorePageResource ─────────────────────────────────────────────────────

    public function test_store_page_resource_uses_page_model(): void
    {
        $this->assertEquals(Page::class, StorePageResource::getModel());
    }

    public function test_store_page_resource_navigation_group_is_marketing(): void
    {
        $this->assertEquals('Marketing', StorePageResource::getNavigationGroup());
    }

    public function test_store_page_resource_has_navigation_icon(): void
    {
        $this->assertEquals('heroicon-o-document-text', StorePageResource::getNavigationIcon());
    }

    public function test_store_page_resource_plural_label_is_pagine(): void
    {
        $this->assertEquals('Pagine', StorePageResource::getPluralModelLabel());
    }

    public function test_store_page_resource_registers_list_create_edit_pages(): void
    {
        $pages = StorePageResource::getPages();

        $this->assertArrayHasKey('index', $pages);
        $this->assertArrayHasKey('create', $pages);
        $this->assertArrayHasKey('edit', $pages);
    }

    public function test_create_store_page_references_correct_resource(): void
    {
        $this->assertEquals(
            StorePageResource::class,
            (new \ReflectionClass(CreateStorePage::class))
                ->getProperty('resource')
                ->getValue()
        );
    }

    public function test_edit_store_page_references_correct_resource(): void
    {
        $this->assertEquals(
            StorePageResource::class,
            (new \ReflectionClass(EditStorePage::class))
                ->getProperty('resource')
                ->getValue()
        );
    }

    public function test_content_json_array_is_preserved_through_update(): void
    {
        $page = $this->makePage(['content' => []]);

        $newContent = [
            ['type' => 'hero',    'data' => ['heading' => 'Benvenuto']],
            ['type' => 'richtext', 'data' => ['body' => '<p>Testo</p>']],
        ];

        $page->update(['content' => $newContent]);

        $this->assertEquals($newContent, $page->fresh()->content);
    }
}
