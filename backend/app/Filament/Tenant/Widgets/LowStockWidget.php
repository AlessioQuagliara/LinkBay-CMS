<?php

declare(strict_types=1);

namespace App\Filament\Tenant\Widgets;

use App\Filament\Tenant\Resources\ProductResource;
use App\Models\Tenant\Product;
use Filament\Forms;
use Filament\Tables;
use Filament\Tables\Table;
use Filament\Widgets\TableWidget as BaseWidget;

class LowStockWidget extends BaseWidget
{
    protected static ?int $sort = 5;

    protected static ?string $heading = 'Prodotti a rischio scorte';

    protected int|string|array $columnSpan = 'full';

    protected static int $threshold = 5;

    public static function canView(): bool
    {
        return Product::where('is_active', true)
            ->where('track_quantity', true)
            ->where('stock', '<=', static::$threshold)
            ->exists();
    }

    public function table(Table $table): Table
    {
        return $table
            ->query(
                Product::where('is_active', true)
                    ->where('track_quantity', true)
                    ->where('stock', '<=', static::$threshold)
                    ->orderBy('stock')
            )
            ->columns([
                Tables\Columns\TextColumn::make('name')
                    ->label('Prodotto')
                    ->url(fn (Product $record) => ProductResource::getUrl('edit', ['record' => $record]))
                    ->weight('medium'),
                Tables\Columns\TextColumn::make('sku')
                    ->label('SKU')
                    ->fontFamily('mono')
                    ->color('gray'),
                Tables\Columns\TextColumn::make('stock')
                    ->label('Stock')
                    ->badge()
                    ->color(fn ($state) => (int) $state <= 0 ? 'danger' : 'warning'),
                Tables\Columns\TextColumn::make('quantity')
                    ->label('Quantità')
                    ->badge()
                    ->color('gray'),
            ])
            ->actions([
                Tables\Actions\Action::make('update_stock')
                    ->label('Aggiorna')
                    ->icon('heroicon-o-pencil')
                    ->form([
                        Forms\Components\TextInput::make('stock')
                            ->label('Nuovo stock')
                            ->integer()
                            ->minValue(0)
                            ->required(),
                        Forms\Components\TextInput::make('quantity')
                            ->label('Nuova quantità')
                            ->integer()
                            ->minValue(0),
                    ])
                    ->fillForm(fn (Product $record) => [
                        'stock' => $record->stock,
                        'quantity' => $record->quantity,
                    ])
                    ->action(function (Product $record, array $data): void {
                        $record->update(array_filter($data, fn ($v) => $v !== null));
                    }),
            ])
            ->emptyStateHeading('Nessun prodotto a rischio')
            ->emptyStateIcon('heroicon-o-check-circle')
            ->paginated(false);
    }
}
