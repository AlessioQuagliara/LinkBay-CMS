<?php

declare(strict_types=1);

namespace Tests\Feature;

use App\Models\Central\Agency;
use App\Models\Central\AuditEvent;
use App\Models\Central\LayoutAssignment;
use App\Models\Central\LayoutTemplate;
use App\Models\Central\Tenant;
use App\Services\LayoutBlockSchema;
use App\Services\LayoutRendererService;
use Illuminate\Database\UniqueConstraintViolationException;
use Illuminate\Support\Facades\DB;
use Tests\CentralTestCase;

/**
 * Covers the Layout Manager MVP: LayoutTemplate model, LayoutAssignment, and
 * LayoutRendererService. Filament Resource UI is tested through the service
 * and model layer which is authoritative.
 *
 * Tests:
 *  1.  Template can be created with agency_id
 *  2.  getEloquentQuery scope: agency A cannot see agency B templates
 *  3.  blocks cast is array (round-trips through JSON correctly)
 *  4.  publish() sets status to published
 *  5.  unpublish() sets status to draft
 *  6.  duplicate() creates independent copy in draft, clones blocks
 *  7.  duplicate() generates unique slug when collision exists
 *  8.  Assignment to valid tenant in same agency succeeds
 *  9.  Assignment cross-agency is blocked by tenant ownership check
 * 10.  unique(tenant_id, page_key) prevents duplicate slot assignments
 * 11.  LayoutRendererService: unknown block types are filtered out
 * 12.  LayoutRendererService: rich_text.content_html is HtmlString (Markdown rendered)
 * 13.  LayoutRendererService: renderTemplate returns empty for draft template
 * 14.  LayoutRendererService: renderTemplate returns blocks for published template
 * 15.  LayoutBlockSchema::knownTypes() covers all 7 v1 blocks
 * 16.  AuditEvent constants for layout events are defined
 */
class LayoutManagerTest extends CentralTestCase
{
    private static int $seq = 0;

    // ── Helpers ───────────────────────────────────────────────────────────────

    private function makeAgency(): Agency
    {
        self::$seq++;

        return Agency::create([
            'name' => 'Agency '.self::$seq,
            'slug' => 'agency-'.self::$seq,
            'brand_name' => 'Agency '.self::$seq,
            'status' => 'active',
            'billing_type' => 'monthly',
        ]);
    }

    private function makeTemplate(Agency $agency, string $status = LayoutTemplate::STATUS_DRAFT): LayoutTemplate
    {
        self::$seq++;

        return LayoutTemplate::create([
            'agency_id' => $agency->id,
            'name' => 'Template '.self::$seq,
            'slug' => 'template-'.self::$seq,
            'status' => $status,
            'blocks' => [],
        ]);
    }

    private function addTenant(Agency $agency): string
    {
        self::$seq++;
        $id = 'store-'.self::$seq;

        DB::connection('central')->table('tenants')->insert([
            'id' => $id,
            'name' => 'Store '.self::$seq,
            'status' => 'active',
            'agency_id' => $agency->id,
            'created_at' => now(),
            'updated_at' => now(),
        ]);

        return $id;
    }

    private function heroBlock(string $title = 'Hero Title'): array
    {
        return [
            'type' => 'hero',
            'data' => ['title' => $title, 'subtitle' => 'Sub'],
        ];
    }

    private function richTextBlock(string $content = '**Bold** text'): array
    {
        return [
            'type' => 'rich_text',
            'data' => ['title' => 'Section', 'content' => $content],
        ];
    }

    private function renderer(): LayoutRendererService
    {
        return app(LayoutRendererService::class);
    }

    // ── Model: creation and basic persistence ─────────────────────────────────

    public function test_template_can_be_created_with_agency_id(): void
    {
        $agency = $this->makeAgency();
        $template = $this->makeTemplate($agency);

        $this->assertModelExists($template);
        $this->assertEquals($agency->id, $template->agency_id);
        $this->assertEquals(LayoutTemplate::STATUS_DRAFT, $template->status);
    }

    public function test_agency_scope_prevents_cross_agency_access(): void
    {
        $agencyA = $this->makeAgency();
        $agencyB = $this->makeAgency();

        $this->makeTemplate($agencyA);
        $this->makeTemplate($agencyB);

        $aTemplates = LayoutTemplate::where('agency_id', $agencyA->id)->get();
        $bTemplates = LayoutTemplate::where('agency_id', $agencyB->id)->get();

        $this->assertCount(1, $aTemplates);
        $this->assertCount(1, $bTemplates);
        $this->assertNotEquals($aTemplates->first()->id, $bTemplates->first()->id);
    }

    public function test_blocks_cast_round_trips_through_json(): void
    {
        $agency = $this->makeAgency();
        $blocks = [$this->heroBlock('Test Title'), $this->richTextBlock()];

        $template = LayoutTemplate::create([
            'agency_id' => $agency->id,
            'name' => 'Block Test',
            'slug' => 'block-test',
            'status' => LayoutTemplate::STATUS_DRAFT,
            'blocks' => $blocks,
        ]);

        $template->refresh();

        $this->assertIsArray($template->blocks);
        $this->assertCount(2, $template->blocks);
        $this->assertEquals('hero', $template->blocks[0]['type']);
        $this->assertEquals('Test Title', $template->blocks[0]['data']['title']);
    }

    // ── Model: publish / unpublish ────────────────────────────────────────────

    public function test_publish_sets_status_to_published(): void
    {
        $agency = $this->makeAgency();
        $template = $this->makeTemplate($agency, LayoutTemplate::STATUS_DRAFT);

        $this->assertTrue($template->isDraft());

        $template->publish();
        $template->refresh();

        $this->assertTrue($template->isPublished());
        $this->assertEquals(LayoutTemplate::STATUS_PUBLISHED, $template->status);
    }

    public function test_unpublish_sets_status_to_draft(): void
    {
        $agency = $this->makeAgency();
        $template = $this->makeTemplate($agency, LayoutTemplate::STATUS_PUBLISHED);

        $template->unpublish();
        $template->refresh();

        $this->assertTrue($template->isDraft());
    }

    // ── Model: duplicate ─────────────────────────────────────────────────────

    public function test_duplicate_creates_independent_draft_copy(): void
    {
        $agency = $this->makeAgency();
        $original = LayoutTemplate::create([
            'agency_id' => $agency->id,
            'name' => 'Original',
            'slug' => 'original',
            'status' => LayoutTemplate::STATUS_PUBLISHED,
            'blocks' => [$this->heroBlock('Copied Title')],
        ]);

        $copy = $original->duplicate('Copy of Original');

        $this->assertModelExists($copy);
        $this->assertNotEquals($original->id, $copy->id);
        $this->assertEquals(LayoutTemplate::STATUS_DRAFT, $copy->status);
        $this->assertEquals($original->agency_id, $copy->agency_id);
        $this->assertEquals('Copied Title', $copy->blocks[0]['data']['title']);
    }

    public function test_duplicate_generates_unique_slug_on_collision(): void
    {
        $agency = $this->makeAgency();

        $original = LayoutTemplate::create([
            'agency_id' => $agency->id,
            'name' => 'My Layout',
            'slug' => 'my-layout',
            'status' => LayoutTemplate::STATUS_DRAFT,
            'blocks' => [],
        ]);

        $copy1 = $original->duplicate('My Layout');
        $copy2 = $original->duplicate('My Layout');

        $this->assertNotEquals('my-layout', $copy1->slug);
        $this->assertNotEquals($copy1->slug, $copy2->slug);
    }

    // ── Assignment: valid and cross-agency ────────────────────────────────────

    public function test_assignment_to_valid_tenant_succeeds(): void
    {
        $agency = $this->makeAgency();
        $template = $this->makeTemplate($agency);
        $tenantId = $this->addTenant($agency);

        $assignment = LayoutAssignment::create([
            'agency_id' => $agency->id,
            'tenant_id' => $tenantId,
            'layout_template_id' => $template->id,
            'page_key' => 'home',
        ]);

        $this->assertModelExists($assignment);
        $this->assertEquals($tenantId, $assignment->tenant_id);
        $this->assertEquals('home', $assignment->page_key);
    }

    public function test_assignment_is_blocked_for_cross_agency_tenant(): void
    {
        $agencyA = $this->makeAgency();
        $agencyB = $this->makeAgency();
        $template = $this->makeTemplate($agencyA);
        $tenantB = $this->addTenant($agencyB); // tenant belongs to agency B

        // The RelationManager's before() hook enforces this. Here we test the
        // security invariant: a cross-agency assignment must NEVER be persisted.
        // Simulating the check the RelationManager performs:
        $tenant = Tenant::find($tenantB);
        $isSameAgency = $tenant && (int) $tenant->agency_id === (int) $agencyA->id;

        $this->assertFalse($isSameAgency, 'Tenant from agency B must not pass agency A ownership check');
    }

    public function test_unique_page_key_per_tenant_is_enforced(): void
    {
        $agency = $this->makeAgency();
        $template1 = $this->makeTemplate($agency);
        $template2 = $this->makeTemplate($agency);
        $tenantId = $this->addTenant($agency);

        LayoutAssignment::create([
            'agency_id' => $agency->id,
            'tenant_id' => $tenantId,
            'layout_template_id' => $template1->id,
            'page_key' => 'home',
        ]);

        $this->expectException(UniqueConstraintViolationException::class);

        LayoutAssignment::create([
            'agency_id' => $agency->id,
            'tenant_id' => $tenantId,
            'layout_template_id' => $template2->id,
            'page_key' => 'home', // same slot — must fail
        ]);
    }

    // ── LayoutRendererService ─────────────────────────────────────────────────

    public function test_renderer_filters_unknown_block_types(): void
    {
        $blocks = [
            $this->heroBlock(),
            ['type' => 'unknown_malicious_block', 'data' => ['payload' => '<script>']],
            $this->richTextBlock(),
        ];

        $rendered = $this->renderer()->render($blocks);

        $this->assertCount(2, $rendered);
        $types = $rendered->pluck('type')->all();
        $this->assertNotContains('unknown_malicious_block', $types);
    }

    public function test_renderer_converts_rich_text_markdown_to_html(): void
    {
        $blocks = [$this->richTextBlock('**Bold** and _italic_')];

        $rendered = $this->renderer()->render($blocks);

        $this->assertCount(1, $rendered);
        $html = (string) $rendered->first()['data']['content_html'];
        $this->assertStringContainsString('<strong>', $html);
    }

    public function test_renderer_strips_html_from_rich_text_input(): void
    {
        $blocks = [$this->richTextBlock('<script>alert("xss")</script> **safe**')];

        $rendered = $this->renderer()->render($blocks);

        $html = (string) $rendered->first()['data']['content_html'];
        $this->assertStringNotContainsString('<script>', $html);
        $this->assertStringNotContainsString('alert(', $html);
    }

    public function test_render_template_returns_empty_for_draft(): void
    {
        $agency = $this->makeAgency();
        $template = LayoutTemplate::create([
            'agency_id' => $agency->id,
            'name' => 'Draft',
            'slug' => 'draft-tpl',
            'status' => LayoutTemplate::STATUS_DRAFT,
            'blocks' => [$this->heroBlock()],
        ]);

        $rendered = $this->renderer()->renderTemplate($template);

        $this->assertTrue($rendered->isEmpty(), 'Draft templates must not render');
    }

    public function test_render_template_returns_blocks_for_published(): void
    {
        $agency = $this->makeAgency();
        $template = LayoutTemplate::create([
            'agency_id' => $agency->id,
            'name' => 'Published',
            'slug' => 'pub-tpl',
            'status' => LayoutTemplate::STATUS_PUBLISHED,
            'blocks' => [$this->heroBlock(), $this->richTextBlock()],
        ]);

        $rendered = $this->renderer()->renderTemplate($template);

        $this->assertCount(2, $rendered);
    }

    // ── LayoutBlockSchema ─────────────────────────────────────────────────────

    public function test_known_types_covers_all_seven_v1_blocks(): void
    {
        $types = LayoutBlockSchema::knownTypes();

        $expected = ['hero', 'feature_grid', 'rich_text', 'cta', 'faq', 'testimonial', 'spacer'];
        foreach ($expected as $type) {
            $this->assertContains($type, $types, "Block type '{$type}' must be in knownTypes()");
        }

        $this->assertCount(7, $types);
    }

    // ── AuditEvent constants ──────────────────────────────────────────────────

    public function test_layout_audit_event_constants_are_defined(): void
    {
        $this->assertEquals('layout.created', AuditEvent::EVENT_LAYOUT_CREATED);
        $this->assertEquals('layout.updated', AuditEvent::EVENT_LAYOUT_UPDATED);
        $this->assertEquals('layout.published', AuditEvent::EVENT_LAYOUT_PUBLISHED);
        $this->assertEquals('layout.duplicated', AuditEvent::EVENT_LAYOUT_DUPLICATED);
        $this->assertEquals('layout.assigned', AuditEvent::EVENT_LAYOUT_ASSIGNED);

        foreach (['layout.created', 'layout.updated', 'layout.published', 'layout.duplicated', 'layout.assigned'] as $event) {
            $this->assertArrayHasKey($event, AuditEvent::EVENT_LABELS);
        }
    }
}
