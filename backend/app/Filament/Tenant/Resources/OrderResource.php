<?php

namespace App\Filament\Tenant\Resources;

use App\Events\Tenant\OrderShipped;
use App\Filament\Tenant\Resources\OrderResource\Pages;
use App\Models\Tenant\Order;
use App\Services\Tenant\StorePaymentService;
use Filament\Actions\Action;
use Filament\Actions\ViewAction;
use Filament\Forms;
use Filament\Infolists;
use Filament\Notifications\Notification;
use Filament\Resources\Resource;
use Filament\Schemas\Schema;
use Filament\Tables;
use Filament\Tables\Table;

class OrderResource extends Resource
{
    protected static ?string $model = Order::class;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-shopping-cart';

    protected static string|\UnitEnum|null $navigationGroup = 'Vendite';

    protected static ?string $modelLabel = 'Ordine';

    protected static ?string $pluralModelLabel = 'Ordini';

    protected static ?int $navigationSort = 1;

    public static function getNavigationBadge(): ?string
    {
        $count = static::getModel()::where('status', 'pending')->count();

        return $count > 0 ? (string) $count : null;
    }

    public static function getNavigationBadgeColor(): string|array|null
    {
        return 'warning';
    }

    public static function getNavigationBadgeTooltip(): ?string
    {
        return 'Ordini in attesa di conferma';
    }

    public static function form(Schema $schema): Schema
    {
        return $schema->schema([]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->columns([
                Tables\Columns\TextColumn::make('id')
                    ->label('#')
                    ->formatStateUsing(fn ($state) => '#'.str_pad($state, 4, '0', STR_PAD_LEFT))
                    ->searchable()
                    ->sortable(),
                Tables\Columns\TextColumn::make('customer.name')
                    ->label('Cliente')
                    ->searchable(),
                Tables\Columns\TextColumn::make('status')
                    ->label('Stato')
                    ->badge()
                    ->color(fn (string $state) => match ($state) {
                        'pending' => 'gray',
                        'confirmed' => 'info',
                        'processing' => 'warning',
                        'shipped' => 'primary',
                        'delivered' => 'success',
                        'cancelled' => 'danger',
                        'refunded' => 'orange',
                        default => 'gray',
                    }),
                Tables\Columns\TextColumn::make('total')
                    ->label('Totale')
                    ->money('EUR')
                    ->sortable(),
                Tables\Columns\TextColumn::make('payment_status')
                    ->label('Pagamento')
                    ->badge()
                    ->color(fn (string $state) => match ($state) {
                        'paid' => 'success',
                        'pending' => 'warning',
                        'failed' => 'danger',
                        'partially_refunded' => 'orange',
                        'refunded' => 'gray',
                        default => 'gray',
                    })
                    ->formatStateUsing(fn (string $state) => match ($state) {
                        'paid' => 'Pagato',
                        'pending' => 'In attesa',
                        'failed' => 'Fallito',
                        'partially_refunded' => 'Rimborsato parzialmente',
                        'refunded' => 'Rimborsato',
                        default => $state,
                    }),
                Tables\Columns\TextColumn::make('created_at')
                    ->label('Data')
                    ->dateTime('d/m/Y H:i')
                    ->sortable(),
            ])
            ->filters([
                Tables\Filters\SelectFilter::make('payment_status')
                    ->label('Stato pagamento')
                    ->options([
                        'paid' => 'Pagato',
                        'pending' => 'In attesa',
                        'failed' => 'Fallito',
                        'partially_refunded' => 'Rimborsato parz.',
                        'refunded' => 'Rimborsato',
                    ]),
                Tables\Filters\SelectFilter::make('status')
                    ->label('Stato')
                    ->options([
                        'pending' => 'In attesa',
                        'confirmed' => 'Confermato',
                        'processing' => 'In lavorazione',
                        'shipped' => 'Spedito',
                        'delivered' => 'Consegnato',
                        'cancelled' => 'Annullato',
                        'refunded' => 'Rimborsato',
                    ]),
                Tables\Filters\SelectFilter::make('payment_status')
                    ->label('Stato pagamento')
                    ->options(['paid' => 'Pagato', 'pending' => 'In attesa', 'failed' => 'Fallito']),
                Tables\Filters\Filter::make('created_at')
                    ->form([
                        Forms\Components\DatePicker::make('from')->label('Dal'),
                        Forms\Components\DatePicker::make('to')->label('Al'),
                    ])
                    ->query(fn ($query, array $data) => $query
                        ->when($data['from'], fn ($q) => $q->whereDate('created_at', '>=', $data['from']))
                        ->when($data['to'], fn ($q) => $q->whereDate('created_at', '<=', $data['to']))
                    ),
            ])
            ->actions([
                ViewAction::make(),
                Action::make('update_status')
                    ->label('Aggiorna stato')
                    ->icon('heroicon-o-arrow-path')
                    ->form([
                        Forms\Components\Select::make('status')
                            ->label('Nuovo stato')
                            ->options([
                                'confirmed' => 'Confermato',
                                'processing' => 'In lavorazione',
                                'shipped' => 'Spedito',
                                'delivered' => 'Consegnato',
                                'cancelled' => 'Annullato',
                                'refunded' => 'Rimborsato',
                            ])
                            ->required(),
                        Forms\Components\TextInput::make('tracking_number')
                            ->label('Tracking number'),
                    ])
                    ->action(fn (Order $record, array $data) => $record->update($data)),

                Action::make('mark_shipped')
                    ->label('Segna come spedito')
                    ->icon('heroicon-o-truck')
                    ->color('info')
                    ->visible(fn (Order $record): bool => in_array($record->status, [
                        Order::STATUS_CONFIRMED,
                        Order::STATUS_PROCESSING,
                    ], true))
                    ->form([
                        Forms\Components\TextInput::make('tracking_number')
                            ->label('Numero di tracking')
                            ->required()
                            ->maxLength(100),
                        Forms\Components\TextInput::make('carrier_name')
                            ->label('Corriere')
                            ->default('DHL')
                            ->required()
                            ->maxLength(100),
                        Forms\Components\TextInput::make('tracking_url')
                            ->label('URL di tracking')
                            ->url()
                            ->nullable(),
                    ])
                    ->action(function (Order $record, array $data): void {
                        $record->update([
                            'status' => Order::STATUS_SHIPPED,
                            'tracking_number' => $data['tracking_number'],
                        ]);

                        event(new OrderShipped(
                            $record,
                            $data['tracking_number'],
                            $data['carrier_name'],
                            $data['tracking_url'] ?? '',
                        ));

                        Notification::make()->title('Ordine segnato come spedito')->success()->send();
                    }),

                Action::make('capture_payment')
                    ->label('Cattura pagamento')
                    ->icon('heroicon-o-check-circle')
                    ->color('success')
                    ->requiresConfirmation()
                    ->visible(fn (Order $record): bool => $record->payment_status === Order::PAYMENT_STATUS_PENDING
                        && $record->stripe_payment_intent_id !== null
                    )
                    ->action(function (Order $record): void {
                        try {
                            app(StorePaymentService::class)->capturePayment($record);
                            Notification::make()->title('Pagamento catturato')->success()->send();
                        } catch (\Throwable $e) {
                            Notification::make()->title('Errore: '.$e->getMessage())->danger()->send();
                        }
                    }),

                Action::make('refund')
                    ->label('Rimborsa')
                    ->icon('heroicon-o-arrow-uturn-left')
                    ->color('warning')
                    ->visible(fn (Order $record): bool => in_array($record->payment_status, [
                        Order::PAYMENT_STATUS_PAID,
                        Order::PAYMENT_STATUS_PARTIALLY_REFUNDED,
                    ], true)
                    )
                    ->form([
                        Forms\Components\TextInput::make('amount')
                            ->label('Importo da rimborsare (€)')
                            ->helperText('Lascia vuoto per rimborso totale')
                            ->numeric()
                            ->minValue(0.01)
                            ->nullable(),
                        Forms\Components\Select::make('reason')
                            ->label('Motivo')
                            ->options([
                                'requested_by_customer' => 'Richiesta del cliente',
                                'duplicate' => 'Pagamento duplicato',
                                'fraudulent' => 'Frode',
                            ])
                            ->nullable(),
                    ])
                    ->action(function (Order $record, array $data): void {
                        try {
                            app(StorePaymentService::class)->refundOrder(
                                $record,
                                ! empty($data['amount']) ? (float) $data['amount'] : null,
                                $data['reason'] ?? null,
                            );
                            Notification::make()->title('Rimborso effettuato')->success()->send();
                        } catch (\Throwable $e) {
                            Notification::make()->title('Errore rimborso: '.$e->getMessage())->danger()->send();
                        }
                    }),
            ])
            ->defaultSort('created_at', 'desc');
    }

    public static function infolist(Schema $schema): Schema
    {
        return $schema->schema([
            Infolists\Components\Section::make('Ordine')
                ->schema([
                    Infolists\Components\TextEntry::make('id')
                        ->label('Numero ordine')
                        ->formatStateUsing(fn ($state) => '#'.str_pad($state, 4, '0', STR_PAD_LEFT)),
                    Infolists\Components\TextEntry::make('status')
                        ->label('Stato')
                        ->badge(),
                    Infolists\Components\TextEntry::make('created_at')
                        ->label('Data ordine')
                        ->dateTime('d/m/Y H:i'),
                    Infolists\Components\TextEntry::make('notes')
                        ->label('Note')
                        ->columnSpanFull(),
                ])->columns(3),

            Infolists\Components\Section::make('Cliente')
                ->schema([
                    Infolists\Components\TextEntry::make('customer.name')->label('Nome'),
                    Infolists\Components\TextEntry::make('customer.email')->label('Email'),
                    Infolists\Components\TextEntry::make('customer.phone')->label('Telefono'),
                    Infolists\Components\TextEntry::make('shipping_address')
                        ->label('Indirizzo di spedizione')
                        ->formatStateUsing(fn ($state) => is_array($state)
                            ? implode(', ', array_filter($state))
                            : $state
                        ),
                ])->columns(2),

            Infolists\Components\Section::make('Prodotti')
                ->schema([
                    Infolists\Components\RepeatableEntry::make('items')
                        ->label('')
                        ->schema([
                            Infolists\Components\TextEntry::make('name')->label('Prodotto'),
                            Infolists\Components\TextEntry::make('quantity')->label('Qtà'),
                            Infolists\Components\TextEntry::make('price')->label('Prezzo unit.')->money('EUR'),
                            Infolists\Components\TextEntry::make('total')->label('Totale')->money('EUR'),
                        ])->columns(4),
                ]),

            Infolists\Components\Section::make('Totali')
                ->schema([
                    Infolists\Components\TextEntry::make('subtotal')->label('Subtotale')->money('EUR'),
                    Infolists\Components\TextEntry::make('discount_total')->label('Sconto')->money('EUR'),
                    Infolists\Components\TextEntry::make('shipping_total')->label('Spedizione')->money('EUR'),
                    Infolists\Components\TextEntry::make('total')->label('Totale')->money('EUR')->weight('bold'),
                ])->columns(4),

            Infolists\Components\Section::make('Pagamento')
                ->schema([
                    Infolists\Components\TextEntry::make('payment_method')->label('Metodo'),
                    Infolists\Components\TextEntry::make('payment_status')->label('Stato')->badge(),
                    Infolists\Components\TextEntry::make('tracking_number')->label('Tracking'),
                ])->columns(3),
        ]);
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListOrders::route('/'),
            'view' => Pages\ViewOrder::route('/{record}'),
        ];
    }
}
