<?php

declare(strict_types=1);

namespace App\Exports\Tenant;

use App\Models\Tenant\Product;
use Illuminate\Database\Eloquent\Builder;
use Symfony\Component\HttpFoundation\StreamedResponse;

class ProductExport
{
    /** @var list<string> */
    private const HEADERS = [
        'id', 'name', 'description', 'price', 'compare_at_price', 'sku', 'barcode',
        'quantity', 'stock', 'track_quantity', 'requires_shipping', 'weight', 'weight_unit',
        'category_slugs', 'status', 'seo_title', 'seo_description',
        'images_urls', 'created_at', 'updated_at',
    ];

    public function download(?Builder $query = null): StreamedResponse
    {
        $query ??= Product::withTrashed()->with(['categories:id,slug', 'productImages' => fn ($q) => $q->where('is_primary', true)->limit(1)]);

        return response()->streamDownload(
            function () use ($query): void {
                $handle = fopen('php://output', 'w');

                // UTF-8 BOM — Excel italiano riconosce correttamente l'encoding
                fwrite($handle, "\xEF\xBB\xBF");

                fputcsv($handle, self::HEADERS);

                $query->chunk(200, function ($products) use ($handle): void {
                    foreach ($products as $product) {
                        fputcsv($handle, $this->toRow($product));
                    }
                });

                fclose($handle);
            },
            'prodotti_'.now()->format('Y-m-d').'.csv',
            [
                'Content-Type' => 'text/csv; charset=UTF-8',
                'Content-Disposition' => 'attachment',
            ],
        );
    }

    /** @return list<string> */
    private function toRow(Product $product): array
    {
        return [
            $product->id,
            $product->name,
            strip_tags($product->description ?? ''),
            $product->price,
            $product->compare_at_price ?? '',
            $product->sku ?? '',
            $product->barcode ?? '',
            $product->quantity,
            $product->stock,
            $product->track_quantity ? '1' : '0',
            $product->requires_shipping ? '1' : '0',
            $product->weight ?? '',
            $product->weight_unit ?? 'kg',
            $product->categories->pluck('slug')->join('|'),
            $product->is_active ? 'active' : 'inactive',
            $product->seo_title ?? '',
            $product->seo_description ?? '',
            $product->productImages->first()?->url ?? '',
            $product->created_at?->toDateTimeString() ?? '',
            $product->updated_at?->toDateTimeString() ?? '',
        ];
    }

    /** Generate a one-row template CSV for download. */
    public function template(): StreamedResponse
    {
        return response()->streamDownload(
            function (): void {
                $handle = fopen('php://output', 'w');
                fwrite($handle, "\xEF\xBB\xBF");
                fputcsv($handle, self::HEADERS);

                fputcsv($handle, [
                    '', 'Esempio Prodotto', 'Descrizione del prodotto', '29.90', '39.90',
                    'SKU-001', '', '100', '100', '1', '1', '0.5', 'kg',
                    'categoria-1|categoria-2', 'active', '', '', '', '', '',
                ]);

                fclose($handle);
            },
            'template_prodotti.csv',
            ['Content-Type' => 'text/csv; charset=UTF-8'],
        );
    }
}
