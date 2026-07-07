<?php

declare(strict_types=1);

namespace Tests\Feature\Tenant;

use App\Imports\Tenant\ProductImport;
use App\Models\Tenant\Category;
use App\Models\Tenant\Product;
use Tests\TenantTestCase;

class ProductImportTest extends TenantTestCase
{
    private ProductImport $importer;

    private string $tempDir;

    protected function setUp(): void
    {
        parent::setUp();
        $this->importer = new ProductImport;
        $this->tempDir = sys_get_temp_dir();
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private function writeCsv(string $filename, array $rows): string
    {
        $path = $this->tempDir.'/'.$filename;
        $handle = fopen($path, 'w');

        foreach ($rows as $row) {
            fputcsv($handle, $row);
        }

        fclose($handle);

        return $path;
    }

    private function headers(): array
    {
        return ProductImport::COLUMNS;
    }

    private function row(array $overrides = []): array
    {
        $defaults = [
            'name' => 'Test Product',
            'description' => 'A description',
            'price' => '29.90',
            'compare_at_price' => '',
            'sku' => 'TEST-001',
            'barcode' => '',
            'quantity' => '10',
            'track_quantity' => '1',
            'requires_shipping' => '1',
            'weight' => '0.5',
            'weight_unit' => 'kg',
            'category_slugs' => '',
            'status' => 'active',
            'seo_title' => '',
            'seo_description' => '',
        ];

        return array_values(array_merge($defaults, $overrides));
    }

    // ── Tests ─────────────────────────────────────────────────────────────────

    public function test_creates_new_product_from_csv(): void
    {
        $path = $this->writeCsv('import_create.csv', [
            $this->headers(),
            $this->row(['name' => 'Nuovo Prodotto', 'price' => '49.90', 'sku' => 'NP-001']),
        ]);

        $this->importer->import($path);

        $this->assertSame(0, count($this->importer->errors()));
        $this->assertSame(1, $this->importer->createdCount());

        $product = Product::where('sku', 'NP-001')->first();
        $this->assertNotNull($product);
        $this->assertSame('Nuovo Prodotto', $product->name);
        $this->assertEqualsWithDelta(49.90, (float) $product->price, 0.01);
        $this->assertTrue($product->is_active);
    }

    public function test_updates_existing_product_by_sku(): void
    {
        Product::create([
            'name' => 'Old Name',
            'slug' => 'old-name',
            'price' => 10.00,
            'sku' => 'UPDATE-001',
            'stock' => 5,
        ]);

        $path = $this->writeCsv('import_update.csv', [
            $this->headers(),
            $this->row(['name' => 'New Name', 'price' => '99.00', 'sku' => 'UPDATE-001', 'quantity' => '50']),
        ]);

        $this->importer->import($path);

        $this->assertSame(0, count($this->importer->errors()));
        $this->assertSame(0, $this->importer->createdCount());
        $this->assertSame(1, $this->importer->updatedCount());

        $product = Product::where('sku', 'UPDATE-001')->first();
        $this->assertSame('New Name', $product->name);
        $this->assertEqualsWithDelta(99.00, (float) $product->price, 0.01);
    }

    public function test_skips_row_with_missing_name_and_records_error(): void
    {
        $path = $this->writeCsv('import_missing_name.csv', [
            $this->headers(),
            $this->row(['name' => '']),
        ]);

        $this->importer->import($path);

        $this->assertCount(1, $this->importer->errors());
        $this->assertSame(0, $this->importer->createdCount());
    }

    public function test_skips_row_with_invalid_price_and_records_error(): void
    {
        $path = $this->writeCsv('import_bad_price.csv', [
            $this->headers(),
            $this->row(['price' => 'not-a-number']),
        ]);

        $this->importer->import($path);

        $this->assertCount(1, $this->importer->errors());
    }

    public function test_creates_categories_from_slugs(): void
    {
        $path = $this->writeCsv('import_categories.csv', [
            $this->headers(),
            $this->row(['name' => 'Cat Product', 'sku' => 'CAT-001', 'category_slugs' => 'abbigliamento|scarpe']),
        ]);

        $this->importer->import($path);

        $this->assertSame(0, count($this->importer->errors()));

        $product = Product::where('sku', 'CAT-001')->with('categories')->first();
        $this->assertNotNull($product);
        $this->assertCount(2, $product->categories);

        $slugs = $product->categories->pluck('slug')->sort()->values()->all();
        $this->assertSame(['abbigliamento', 'scarpe'], $slugs);
    }

    public function test_syncs_to_existing_category(): void
    {
        Category::create(['name' => 'Esistente', 'slug' => 'esistente', 'is_active' => true]);

        $path = $this->writeCsv('import_existing_category.csv', [
            $this->headers(),
            $this->row(['sku' => 'EXCAT-001', 'category_slugs' => 'esistente']),
        ]);

        $this->importer->import($path);

        $this->assertSame(1, Category::where('slug', 'esistente')->count());
    }

    public function test_processes_multiple_rows(): void
    {
        $path = $this->writeCsv('import_multi.csv', [
            $this->headers(),
            $this->row(['name' => 'Prodotto A', 'sku' => 'MULTI-001']),
            $this->row(['name' => 'Prodotto B', 'sku' => 'MULTI-002']),
            $this->row(['name' => 'Prodotto C', 'sku' => 'MULTI-003']),
        ]);

        $this->importer->import($path);

        $this->assertSame(0, count($this->importer->errors()));
        $this->assertSame(3, $this->importer->createdCount());
        $this->assertSame(3, Product::count());
    }

    public function test_handles_utf8_bom_in_header(): void
    {
        $path = $this->tempDir.'/import_bom.csv';
        $handle = fopen($path, 'w');

        // Write BOM
        fwrite($handle, "\xEF\xBB\xBF");
        fputcsv($handle, $this->headers());
        fputcsv($handle, $this->row(['name' => 'BOM Product', 'sku' => 'BOM-001']));
        fclose($handle);

        $this->importer->import($path);

        $this->assertSame(0, count($this->importer->errors()));
        $this->assertNotNull(Product::where('sku', 'BOM-001')->first());
    }
}
