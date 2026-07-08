<?php

declare(strict_types=1);

namespace App\Filament\Admin\Resources;

use App\Filament\Admin\Resources\FailedJobResource\Pages;
use App\Models\Central\FailedJob;
use Filament\Actions\BulkActionGroup;
use Filament\Actions\DeleteBulkAction;
use Filament\Notifications\Notification;
use Filament\Resources\Resource;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Support\Facades\Artisan;

class FailedJobResource extends Resource
{
    protected static ?string $model = FailedJob::class;

    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-exclamation-triangle';

    protected static string|\UnitEnum|null $navigationGroup = 'Operations';

    protected static ?string $modelLabel = 'Failed Job';

    protected static ?string $pluralModelLabel = 'Failed Jobs';

    protected static ?int $navigationSort = 20;

    public static function getNavigationBadge(): ?string
    {
        return (string) static::getModel()::count() ?: null;
    }

    public static function getNavigationBadgeColor(): ?string
    {
        return 'danger';
    }

    public static function table(Table $table): Table
    {
        return $table
            ->defaultSort('failed_at', 'desc')
            ->columns([
                Tables\Columns\TextColumn::make('job_class')
                    ->label('Job')
                    ->state(fn (FailedJob $record) => $record->jobClass())
                    ->searchable(query: fn ($query, string $search) => $query->where('payload', 'like', "%{$search}%")),

                Tables\Columns\TextColumn::make('queue')
                    ->label('Queue')
                    ->badge()
                    ->color('gray'),

                Tables\Columns\TextColumn::make('exception_summary')
                    ->label('Exception')
                    ->state(fn (FailedJob $record) => $record->exceptionSummary())
                    ->limit(80)
                    ->tooltip(fn (FailedJob $record) => $record->exceptionSummary())
                    ->color('danger'),

                Tables\Columns\TextColumn::make('failed_at')
                    ->label('Failed at')
                    ->dateTime('d/m/Y H:i')
                    ->sortable(),
            ])
            ->actions([
                Tables\Actions\Action::make('retry')
                    ->label('Retry')
                    ->icon('heroicon-o-arrow-path')
                    ->color('warning')
                    ->requiresConfirmation()
                    ->action(function (FailedJob $record): void {
                        Artisan::call('queue:retry', ['id' => [$record->uuid]]);
                        Notification::make()->title('Job re-queued')->success()->send();
                    }),

                Tables\Actions\DeleteAction::make()
                    ->label('Forget'),
            ])
            ->bulkActions([
                BulkActionGroup::make([
                    DeleteBulkAction::make()->label('Forget selected'),
                ]),
            ])
            ->emptyStateHeading('No failed jobs')
            ->emptyStateDescription('Every dispatched job (webhook processing, tenant provisioning, notifications) has completed successfully.')
            ->emptyStateIcon('heroicon-o-check-circle');
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListFailedJobs::route('/'),
        ];
    }
}
