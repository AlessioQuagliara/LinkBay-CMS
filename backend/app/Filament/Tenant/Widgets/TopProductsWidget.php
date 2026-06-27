<?php

declare(strict_types=1);

namespace App\Filament\Tenant\Widgets;

use App\Filament\Tenant\Resources\ProductResource;
use App\Models\Tenant\Product;
use App\Services\Tenant\AnalyticsService;
use Filament\Tables;
use Filament\Tables\Table;
use Filament\Widgets\TableWidget as BaseWidget;
use Illuminate\Support\Carbon;
use Livewire\Attributes\On;

class TopProductsWidget extends BaseWidget
{
    protected static ?int $sort = 4;

    protected static ?string $heading = 'Prodotti più venduti';

    protected int|string|array $columnSpan = 'full';

    public string $period = '30';

    public ?string $analyticsFrom = null;

    public ?string $analyticsTo = null;

    #[On('analyticsDateChanged')]
    public function updateDateRange(string $from, string $to): void
    {
        $this->analyticsFrom = $from;
        $this->analyticsTo = $to;
        $this->period = 'custom';
    }

    protected function getFilters(): ?array
    {
        return [
            '7' => 'Ultimi 7 giorni',
            '30' => 'Ultimi 30 giorni',
            '90' => 'Ultimi 3 mesi',
        ];
    }

    public function table(Table $table): Table
    {
        $filter = $this->getFilterValue('period') ?? '30';
        [$from, $to] = $this->resolveDateRange($filter);

        $topProducts = app(AnalyticsService::class)->getTopProducts($from, $to, 10);
        $productIds = $topProducts->pluck('product_id')->all();

        // Attach analytics data to each product record
        $analyticsMap = $topProducts->keyBy('product_id');

        return $table
            ->query(
                Product::whereIn('id', $productIds)
                    ->with(['productImages' => fn ($q) => $q->where('is_primary', true)->limit(1)])
            )
            ->defaultSort(fn ($query) => $query->orderByRaw('FIELD(id, '.implode(',', $productIds ?: [0]).')'))
            ->columns([
                Tables\Columns\ImageColumn::make('productImages.0.url')
                    ->label('')
                    ->size(40)
                    ->defaultImageUrl(fn () => null)
                    ->width(40)
                    ->height(40),
                Tables\Columns\TextColumn::make('name')
                    ->label('Prodotto')
                    ->url(fn (Product $record) => ProductResource::getUrl('edit', ['record' => $record]))
                    ->weight('medium'),
                Tables\Columns\TextColumn::make('sku')
                    ->label('SKU')
                    ->fontFamily('mono')
                    ->color('gray'),
                Tables\Columns\TextColumn::make('units_sold')
                    ->label('Unità vendute')
                    ->getStateUsing(fn (Product $record) => $analyticsMap->get($record->id)['units_sold'] ?? 0)
                    ->badge()
                    ->color('info'),
                Tables\Columns\TextColumn::make('revenue')
                    ->label('Fatturato')
                    ->getStateUsing(fn (Product $record) => $analyticsMap->get($record->id)['revenue'] ?? 0)
                    ->formatStateUsing(fn ($state) => '€ '.number_format((float) $state, 2, ',', '.')),
            ])
            ->paginated(false);
    }

    private function resolveDateRange(string $filter): array
    {
        if ($this->analyticsFrom && $this->analyticsTo) {
            return [Carbon::parse($this->analyticsFrom), Carbon::parse($this->analyticsTo)];
        }

        return [
            now()->subDays((int) $filter - 1)->startOfDay(),
            now()->endOfDay(),
        ];
    }
}
