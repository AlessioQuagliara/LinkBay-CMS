<?php

namespace App\Filament\Admin\Resources;

use App\Filament\Admin\Resources\JobApplicationResource\Pages;
use App\Models\Central\JobApplication;
use App\Models\Central\JobPosition;
use Filament\Forms;
use Filament\Resources\Resource;
use Filament\Schemas\Components\Section;
use Filament\Schemas\Schema;
use Filament\Tables;
use Filament\Tables\Table;

class JobApplicationResource extends Resource
{
    protected static ?string $model = JobApplication::class;
    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-document-text';
    protected static string|\UnitEnum|null $navigationGroup = 'Careers';
    protected static ?string $modelLabel = 'Application';
    protected static ?string $pluralModelLabel = 'Applications';
    protected static ?int $navigationSort = 2;

    public static function getNavigationBadge(): ?string
    {
        return (string) static::getModel()::where('status', 'new')->count() ?: null;
    }

    public static function getNavigationBadgeColor(): ?string
    {
        return 'danger';
    }

    public static function form(Schema $schema): Schema
    {
        return $schema->schema([
            Section::make('Candidate')
                ->schema([
                    Forms\Components\TextInput::make('full_name')->label('Name')->disabled(),
                    Forms\Components\TextInput::make('email')->label('Email')->disabled(),
                    Forms\Components\TextInput::make('phone')->label('Phone')->disabled()->placeholder('—'),
                    Forms\Components\TextInput::make('location')->label('Location')->disabled()->placeholder('—'),
                    Forms\Components\TextInput::make('linkedin_url')
                        ->label('LinkedIn')
                        ->disabled()
                        ->suffixAction(
                            Forms\Components\Actions\Action::make('open_linkedin')
                                ->icon('heroicon-o-arrow-top-right-on-square')
                                ->url(fn ($state) => $state)
                                ->openUrlInNewTab()
                                ->visible(fn ($state) => filled($state))
                        ),
                    Forms\Components\TextInput::make('portfolio_url')
                        ->label('Portfolio / GitHub')
                        ->disabled()
                        ->suffixAction(
                            Forms\Components\Actions\Action::make('open_portfolio')
                                ->icon('heroicon-o-arrow-top-right-on-square')
                                ->url(fn ($state) => $state)
                                ->openUrlInNewTab()
                                ->visible(fn ($state) => filled($state))
                        ),
                ])->columns(2),

            Section::make('Application')
                ->schema([
                    Forms\Components\TextInput::make('position.title')
                        ->label('Applied for')
                        ->disabled(),
                    Forms\Components\Select::make('status')
                        ->label('Status')
                        ->options([
                            'new'         => 'New',
                            'reviewing'   => 'Reviewing',
                            'shortlisted' => 'Shortlisted',
                            'rejected'    => 'Rejected',
                            'closed'      => 'Closed',
                        ])
                        ->required(),
                    Forms\Components\Textarea::make('motivation')
                        ->label('Motivation')
                        ->disabled()
                        ->rows(4)
                        ->columnSpanFull(),
                    Forms\Components\Textarea::make('experience_summary')
                        ->label('Relevant experience')
                        ->disabled()
                        ->rows(4)
                        ->columnSpanFull(),
                ])->columns(2),

            Section::make('Admin notes')
                ->schema([
                    Forms\Components\Textarea::make('admin_notes')
                        ->label('Internal notes')
                        ->rows(3)
                        ->placeholder('Notes visible only to admins...')
                        ->columnSpanFull(),
                ]),
        ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->defaultSort('created_at', 'desc')
            ->columns([
                Tables\Columns\TextColumn::make('full_name')
                    ->label('Candidate')
                    ->searchable()
                    ->description(fn ($record) => $record->email),
                Tables\Columns\TextColumn::make('position.title')
                    ->label('Position')
                    ->searchable()
                    ->description(fn ($record) => $record->position?->department),
                Tables\Columns\SelectColumn::make('status')
                    ->label('Status')
                    ->options([
                        'new'         => 'New',
                        'reviewing'   => 'Reviewing',
                        'shortlisted' => 'Shortlisted',
                        'rejected'    => 'Rejected',
                        'closed'      => 'Closed',
                    ])
                    ->sortable(),
                Tables\Columns\TextColumn::make('created_at')
                    ->label('Submitted')
                    ->dateTime('d M Y, H:i')
                    ->sortable(),
            ])
            ->filters([
                Tables\Filters\SelectFilter::make('status')
                    ->options([
                        'new'         => 'New',
                        'reviewing'   => 'Reviewing',
                        'shortlisted' => 'Shortlisted',
                        'rejected'    => 'Rejected',
                        'closed'      => 'Closed',
                    ]),
                Tables\Filters\SelectFilter::make('job_position_id')
                    ->label('Position')
                    ->relationship('position', 'title')
                    ->searchable()
                    ->preload(),
                Tables\Filters\SelectFilter::make('department')
                    ->label('Department')
                    ->options(fn () => JobPosition::query()
                        ->distinct()
                        ->pluck('department', 'department')
                        ->toArray()
                    )
                    ->query(fn ($query, $data) =>
                        $data['value']
                            ? $query->whereHas('position', fn ($q) => $q->where('department', $data['value']))
                            : $query
                    ),
            ])
            ->actions([
                \Filament\Actions\EditAction::make()->label('Review'),
                \Filament\Actions\Action::make('download_cv')
                    ->label('CV')
                    ->icon('heroicon-o-document-arrow-down')
                    ->url(fn ($record) => route('admin.careers.cv.download', $record))
                    ->openUrlInNewTab(),
            ])
            ->bulkActions([
                \Filament\Actions\BulkActionGroup::make([
                    \Filament\Actions\DeleteBulkAction::make(),
                ]),
            ]);
    }

    public static function getPages(): array
    {
        return [
            'index' => Pages\ListJobApplications::route('/'),
            'edit'  => Pages\ViewJobApplication::route('/{record}/edit'),
        ];
    }
}
