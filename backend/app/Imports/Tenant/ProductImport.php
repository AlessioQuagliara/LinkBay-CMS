<?php

declare(strict_types=1);

namespace App\Imports\Tenant;

use App\Models\Tenant\Category;
use App\Models\Tenant\Product;
use Illuminate\Support\Enumerable;
use Illuminate\Support\LazyCollection;
use Illuminate\Support\Str;

class ProductImport
{
    /**
     * Expected CSV columns (header row required).
     *
     * @var list<string>
     */
    public const COLUMNS = [
        'name', 'description', 'price', 'compare_at_price', 'sku', 'barcode',
        'quantity', 'track_quantity', 'requires_shipping', 'weight', 'weight_unit',
        'category_slugs', 'status', 'seo_title', 'seo_description',
    ];

    /** @var list<array{row: int, error: string}> */
    private array $errors = [];

    private int $processed = 0;

    private int $created = 0;

    private int $updated = 0;

    /**
     * Process a CSV file path row-by-row using LazyCollection (no memory spike).
     *
     * @param  callable(int $processed, int $total): void  $onProgress
     */
    public function import(string $filePath, ?callable $onProgress = null): void
    {
        $this->errors = [];
        $this->processed = 0;
        $this->created = 0;
        $this->updated = 0;

        $rows = $this->lazyReadCsv($filePath);
        $total = $this->countLines($filePath);

        foreach ($rows->chunk(50) as $chunk) {
            $this->processChunk($chunk);

            if ($onProgress) {
                $onProgress($this->processed, $total);
            }
        }
    }

    /** @return list<array{row: int, error: string}> */
    public function errors(): array
    {
        return $this->errors;
    }

    public function processedCount(): int
    {
        return $this->processed;
    }

    public function createdCount(): int
    {
        return $this->created;
    }

    public function updatedCount(): int
    {
        return $this->updated;
    }

    /** @param  Enumerable<int, array<string, string>>  $chunk */
    private function processChunk(Enumerable $chunk): void
    {
        foreach ($chunk as $rowIndex => $row) {
            try {
                $this->processRow($row, $rowIndex + 2); // +2 = 1-based + header
            } catch (\Throwable $e) {
                $this->errors[] = ['row' => $rowIndex + 2, 'error' => $e->getMessage()];
            }

            $this->processed++;
        }
    }

    /** @param  array<string, string>  $row */
    private function processRow(array $row, int $lineNumber): void
    {
        $name = trim($row['name'] ?? '');

        if ($name === '') {
            $this->errors[] = ['row' => $lineNumber, 'error' => "Riga {$lineNumber}: il campo 'name' è obbligatorio."];

            return;
        }

        $priceRaw = trim($row['price'] ?? '');

        if ($priceRaw === '' || ! is_numeric($priceRaw) || (float) $priceRaw < 0) {
            $this->errors[] = ['row' => $lineNumber, 'error' => "Riga {$lineNumber}: prezzo non valido."];

            return;
        }

        $price = (float) $priceRaw;

        $sku = trim($row['sku'] ?? '');
        $isActive = $this->parseBool($row['status'] ?? 'active', trueValue: 'active');

        $attributes = [
            'name' => $name,
            'description' => $row['description'] ?? null,
            'price' => $price,
            'compare_at_price' => isset($row['compare_at_price']) && $row['compare_at_price'] !== ''
                ? (float) $row['compare_at_price']
                : null,
            'barcode' => $row['barcode'] ?? null,
            'quantity' => isset($row['quantity']) ? (int) $row['quantity'] : 0,
            'track_quantity' => $this->parseBool($row['track_quantity'] ?? '1'),
            'requires_shipping' => $this->parseBool($row['requires_shipping'] ?? '1'),
            'weight' => isset($row['weight']) && $row['weight'] !== '' ? (float) $row['weight'] : null,
            'weight_unit' => $row['weight_unit'] ?? 'kg',
            'is_active' => $isActive,
            'seo_title' => $row['seo_title'] ?? null,
            'seo_description' => $row['seo_description'] ?? null,
            'stock' => isset($row['quantity']) ? (int) $row['quantity'] : 0,
        ];

        if ($sku !== '') {
            $product = Product::where('sku', $sku)->first();

            if ($product) {
                $product->update($attributes);
                $this->updated++;
            } else {
                $attributes['sku'] = $sku;
                $attributes['slug'] = $this->uniqueSlug($name);
                $product = Product::create($attributes);
                $this->created++;
            }
        } else {
            $attributes['slug'] = $this->uniqueSlug($name);
            $product = Product::create($attributes);
            $this->created++;
        }

        // Sync categories from pipe-separated slugs
        $slugsRaw = trim($row['category_slugs'] ?? '');

        if ($slugsRaw !== '') {
            $slugs = array_filter(array_map('trim', explode('|', $slugsRaw)));
            $categoryIds = [];

            foreach ($slugs as $slug) {
                $category = Category::firstOrCreate(
                    ['slug' => $slug],
                    ['name' => Str::title(str_replace('-', ' ', $slug)), 'is_active' => true]
                );
                $categoryIds[] = $category->id;
            }

            $product->categories()->sync($categoryIds);
        }
    }

    private function uniqueSlug(string $name): string
    {
        $base = Str::slug($name);
        $slug = $base;
        $i = 1;

        while (Product::where('slug', $slug)->exists()) {
            $slug = "{$base}-{$i}";
            $i++;
        }

        return $slug;
    }

    private function parseBool(string $value, string $trueValue = '1'): bool
    {
        $lower = strtolower(trim($value));

        if ($trueValue !== '1') {
            return $lower === strtolower($trueValue);
        }

        return in_array($lower, ['1', 'true', 'yes', 'si', 'sì', 'y'], true);
    }

    /**
     * @return LazyCollection<int, array<string, string>>
     */
    private function lazyReadCsv(string $filePath): LazyCollection
    {
        return LazyCollection::make(function () use ($filePath) {
            $handle = fopen($filePath, 'r');

            if ($handle === false) {
                throw new \RuntimeException("Impossibile aprire il file CSV: {$filePath}");
            }

            try {
                $headers = fgetcsv($handle);

                if ($headers === false) {
                    return;
                }

                $headers = array_map('trim', $headers);

                // Strip UTF-8 BOM from first column header if present
                $headers[0] = ltrim($headers[0], "\xEF\xBB\xBF");

                while (($row = fgetcsv($handle)) !== false) {
                    if (count($row) === count($headers)) {
                        yield array_combine($headers, $row);
                    }
                }
            } finally {
                fclose($handle);
            }
        });
    }

    private function countLines(string $filePath): int
    {
        $count = 0;
        $handle = fopen($filePath, 'r');

        if ($handle === false) {
            return 0;
        }

        while (fgets($handle) !== false) {
            $count++;
        }

        fclose($handle);

        return max(0, $count - 1); // exclude header
    }
}
