<?php

declare(strict_types=1);

namespace App\Filament\Admin\Resources;

use App\Filament\Admin\Resources\BillingEventResource\Pages;
use App\Jobs\ProcessStripeWebhookJob;
use App\Models\Central\BillingEvent;
use Filament\Notifications\Notification;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Database\Eloquent\Builder;

/**
 * Ops view over Stripe webhook processing (BillingEvent). Every webhook Stripe sends
 * is written here before its job runs (see StripeWebhookController); this resource
 * surfaces the ones that never finished — stuck (queued too long) or errored — since
 * those otherwise sit silently until `billing:reprocess-stuck-events` retries them.
 */
class BillingEventResource extends Resource
{
    protected static ?string $model = BillingEvent::class;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-signal-slash';

    protected static string|\UnitEnum|null $navigationGroup = 'Operations';

    protected static ?string $modelLabel = 'Webhook Event';

    protected static ?string $pluralModelLabel = 'Stripe Webhooks';

    protected static ?int $navigationSort = 21;

    public static function getEloquentQuery(): Builder
    {
        return parent::getEloquentQuery()->whereNull('processed_at');
    }

    public static function getNavigationBadge(): ?string
    {
        return (string) static::getModel()::whereNull('processed_at')
            ->where('created_at', '<', now()->subMinutes(15))
            ->count() ?: null;
    }

    public static function getNavigationBadgeColor(): ?string
    {
        return 'danger';
    }

    public static function table(Table $table): Table
    {
        return $table
            ->defaultSort('created_at', 'desc')
            ->columns([
                Tables\Columns\TextColumn::make('event_type')
                    ->label('Event type')
                    ->searchable()
                    ->badge(),

                Tables\Columns\TextColumn::make('agency.name')
                    ->label('Agency')
                    ->placeholder('—'),

                Tables\Columns\TextColumn::make('stripe_event_id')
                    ->label('Stripe event')
                    ->copyable(),

                Tables\Columns\TextColumn::make('error')
                    ->label('Error')
                    ->limit(60)
                    ->tooltip(fn (?string $state) => $state)
                    ->placeholder('— (queued, not yet processed)')
                    ->color(fn (?string $state) => $state ? 'danger' : 'warning'),

                Tables\Columns\TextColumn::make('created_at')
                    ->label('Received')
                    ->since()
                    ->dateTime('d/m/Y H:i')
                    ->sortable(),
            ])
            ->actions([
                Tables\Actions\Action::make('reprocess')
                    ->label('Reprocess')
                    ->icon('heroicon-o-arrow-path')
                    ->color('warning')
                    ->requiresConfirmation()
                    ->action(function (BillingEvent $record): void {
                        ProcessStripeWebhookJob::dispatch($record->id);
                        Notification::make()->title('Webhook re-dispatched')->success()->send();
                    }),
            ])
            ->emptyStateHeading('No stuck or unprocessed webhooks')
            ->emptyStateDescription('All Stripe events received have been processed.')
            ->emptyStateIcon('heroicon-o-check-circle');
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListBillingEvents::route('/'),
        ];
    }
}
