<?php

declare(strict_types=1);

namespace App\Exports\Tenant;

use App\Models\Tenant\Order;
use Carbon\Carbon;
use Illuminate\Database\Eloquent\Builder;
use Symfony\Component\HttpFoundation\StreamedResponse;

class OrderExport
{
    /** @var list<string> */
    private const HEADERS = [
        'order_number', 'date', 'customer_name', 'customer_email',
        'status', 'payment_status', 'subtotal', 'shipping', 'discount', 'total',
        'items_count', 'shipping_address',
    ];

    public function download(?Builder $query = null, ?Carbon $from = null, ?Carbon $to = null): StreamedResponse
    {
        $query ??= Order::with(['customer:id,name,email', 'items']);

        if ($from) {
            $query->whereDate('created_at', '>=', $from);
        }

        if ($to) {
            $query->whereDate('created_at', '<=', $to);
        }

        $filename = 'ordini_'.now()->format('Y-m-d').'.csv';

        return response()->streamDownload(
            function () use ($query): void {
                $handle = fopen('php://output', 'w');
                fwrite($handle, "\xEF\xBB\xBF");
                fputcsv($handle, self::HEADERS);

                $query->orderByDesc('created_at')->chunk(200, function ($orders) use ($handle): void {
                    foreach ($orders as $order) {
                        fputcsv($handle, $this->toRow($order));
                    }
                });

                fclose($handle);
            },
            $filename,
            [
                'Content-Type' => 'text/csv; charset=UTF-8',
                'Content-Disposition' => 'attachment',
            ],
        );
    }

    /** @return list<string> */
    private function toRow(Order $order): array
    {
        $shippingAddress = is_array($order->shipping_address)
            ? implode(', ', array_filter([
                $order->shipping_address['street'] ?? $order->shipping_address['address_line_1'] ?? '',
                $order->shipping_address['city'] ?? '',
                $order->shipping_address['postal_code'] ?? $order->shipping_address['zip'] ?? '',
                $order->shipping_address['country'] ?? $order->shipping_address['country_code'] ?? '',
            ]))
            : '';

        return [
            '#'.str_pad((string) $order->id, 4, '0', STR_PAD_LEFT),
            $order->created_at?->format('d/m/Y H:i') ?? '',
            $order->customer?->name ?? '',
            $order->customer?->email ?? '',
            $order->status,
            $order->payment_status ?? '',
            number_format((float) $order->subtotal, 2, '.', ''),
            number_format((float) $order->shipping_total, 2, '.', ''),
            number_format((float) $order->discount_total, 2, '.', ''),
            number_format((float) $order->total, 2, '.', ''),
            $order->items?->count() ?? 0,
            $shippingAddress,
        ];
    }
}
