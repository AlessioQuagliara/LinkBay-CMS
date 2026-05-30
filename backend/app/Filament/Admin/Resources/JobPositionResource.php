<?php

namespace App\Filament\Admin\Resources;

use App\Filament\Admin\Resources\JobPositionResource\Pages;
use App\Models\Central\JobPosition;
use Filament\Forms;
use Filament\Resources\Resource;
use Filament\Schemas\Components\Section;
use Filament\Schemas\Components\Utilities\Set;
use Filament\Schemas\Schema;
use Filament\Tables;
use Filament\Tables\Table;
use Illuminate\Support\Str;

class JobPositionResource extends Resource
{
    protected static ?string $model = JobPosition::class;
    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-briefcase';
    protected static string|\UnitEnum|null $navigationGroup = 'Careers';
    protected static ?string $modelLabel = 'Job Position';
    protected static ?string $pluralModelLabel = 'Job Positions';
    protected static ?int $navigationSort = 1;

    public static function form(Schema $schema): Schema
    {
        return $schema->schema([
            Section::make('Position details')
                ->schema([
                    Forms\Components\TextInput::make('title')
                        ->label('Title')
                        ->required()
                        ->maxLength(150)
                        ->live(onBlur: true)
                        ->afterStateUpdated(function (string $state, Set $set, string $operation) {
                            if ($operation !== 'create') return;
                            $set('slug', Str::slug($state));
                        }),
                    Forms\Components\TextInput::make('slug')
                        ->label('Slug')
                        ->required()
                        ->unique(JobPosition::class, 'slug', ignoreRecord: true)
                        ->maxLength(150)
                        ->helperText('Used in the public apply URL — must be stable once published.'),
                    Forms\Components\TextInput::make('department')
                        ->label('Department')
                        ->required()
                        ->maxLength(100)
                        ->placeholder('Engineering'),
                    Forms\Components\TextInput::make('location')
                        ->label('Location')
                        ->required()
                        ->maxLength(100)
                        ->placeholder('Remote'),
                    Forms\Components\Select::make('work_mode')
                        ->label('Work mode')
                        ->options([
                            'remote'   => 'Remote',
                            'hybrid'   => 'Hybrid',
                            'on_site'  => 'On-site',
                        ])
                        ->default('remote')
                        ->required(),
                    Forms\Components\Select::make('employment_type')
                        ->label('Employment type')
                        ->options([
                            'full_time'  => 'Full-time',
                            'part_time'  => 'Part-time',
                            'contract'   => 'Contract',
                            'internship' => 'Internship',
                        ])
                        ->default('full_time')
                        ->required(),
                ])->columns(2),

            Section::make('Publishing')
                ->schema([
                    Forms\Components\Select::make('status')
                        ->label('Status')
                        ->options([
                            'draft'     => 'Draft',
                            'published' => 'Published',
                            'archived'  => 'Archived',
                        ])
                        ->default('draft')
                        ->required()
                        ->live()
                        ->afterStateUpdated(function ($state, Set $set) {
                            if ($state === 'published') {
                                $set('published_at', now()->toDateTimeString());
                            }
                        }),
                    Forms\Components\Toggle::make('featured')
                        ->label('Featured')
                        ->default(false)
                        ->helperText('Featured positions appear first on the careers page.'),
                    Forms\Components\TextInput::make('sort_order')
                        ->label('Sort order')
                        ->numeric()
                        ->default(0)
                        ->helperText('Lower number = shown first (within same featured/non-featured group).'),
                    Forms\Components\DateTimePicker::make('published_at')
                        ->label('Published at')
                        ->nullable(),
                ])->columns(2),

            Section::make('Content')
                ->schema([
                    Forms\Components\Textarea::make('summary')
                        ->label('Short summary')
                        ->required()
                        ->rows(2)
                        ->maxLength(500)
                        ->helperText('Shown on the careers listing card — max 500 characters.')
                        ->columnSpanFull(),
                    Forms\Components\Textarea::make('description')
                        ->label('Full description')
                        ->rows(6)
                        ->helperText('Optional extended description shown on the apply page.')
                        ->columnSpanFull(),
                ]),

            Section::make('Requirements & responsibilities')
                ->schema([
                    Forms\Components\Repeater::make('responsibilities')
                        ->label('Responsibilities')
                        ->simple(
                            Forms\Components\TextInput::make('item')
                                ->label('')
                                ->placeholder('Add a responsibility...')
                                ->required()
                        )
                        ->addActionLabel('Add responsibility')
                        ->reorderable()
                        ->collapsible()
                        ->defaultItems(0),
                    Forms\Components\Repeater::make('requirements')
                        ->label('Requirements')
                        ->simple(
                            Forms\Components\TextInput::make('item')
                                ->label('')
                                ->placeholder('Add a requirement...')
                                ->required()
                        )
                        ->addActionLabel('Add requirement')
                        ->reorderable()
                        ->collapsible()
                        ->defaultItems(0),
                    Forms\Components\Repeater::make('nice_to_have')
                        ->label('Nice to have (optional)')
                        ->simple(
                            Forms\Components\TextInput::make('item')
                                ->label('')
                                ->placeholder('Add a nice-to-have...')
                        )
                        ->addActionLabel('Add item')
                        ->reorderable()
                        ->collapsible()
                        ->defaultItems(0),
                ])->columns(1),
        ]);
    }

    public static function table(Table $table): Table
    {
        return $table
            ->modifyQueryUsing(fn ($query) => $query->orderByDesc('featured')->orderBy('sort_order')->orderByDesc('published_at'))
            ->columns([
                Tables\Columns\TextColumn::make('title')
                    ->label('Position')
                    ->searchable()
                    ->sortable()
                    ->description(fn ($record) => $record->department . ' · ' . $record->location),
                Tables\Columns\TextColumn::make('employment_type')
                    ->label('Type')
                    ->badge()
                    ->formatStateUsing(fn ($state) => match($state) {
                        'full_time'  => 'Full-time',
                        'part_time'  => 'Part-time',
                        'contract'   => 'Contract',
                        'internship' => 'Internship',
                        default      => $state,
                    })
                    ->color('info'),
                Tables\Columns\TextColumn::make('work_mode')
                    ->label('Mode')
                    ->badge()
                    ->formatStateUsing(fn ($state) => match($state) {
                        'remote'  => 'Remote',
                        'hybrid'  => 'Hybrid',
                        'on_site' => 'On-site',
                        default   => $state,
                    })
                    ->color('gray'),
                Tables\Columns\IconColumn::make('featured')
                    ->label('⭐')
                    ->boolean()
                    ->trueIcon('heroicon-o-star')
                    ->falseIcon('heroicon-o-minus'),
                Tables\Columns\TextColumn::make('status')
                    ->label('Status')
                    ->badge()
                    ->color(fn ($state) => match($state) {
                        'published' => 'success',
                        'draft'     => 'warning',
                        'archived'  => 'gray',
                        default     => 'gray',
                    }),
                Tables\Columns\TextColumn::make('applications_count')
                    ->label('Applications')
                    ->counts('applications')
                    ->badge()
                    ->color('primary'),
                Tables\Columns\TextColumn::make('published_at')
                    ->label('Published')
                    ->dateTime('d M Y')
                    ->placeholder('—')
                    ->sortable(),
            ])
            ->filters([
                Tables\Filters\SelectFilter::make('status')
                    ->options([
                        'draft'     => 'Draft',
                        'published' => 'Published',
                        'archived'  => 'Archived',
                    ]),
                Tables\Filters\SelectFilter::make('department')
                    ->options(fn () => JobPosition::query()
                        ->distinct()
                        ->pluck('department', 'department')
                        ->toArray()
                    ),
                Tables\Filters\TernaryFilter::make('featured')
                    ->label('Featured only'),
            ])
            ->actions([
                \Filament\Actions\EditAction::make(),
                \Filament\Actions\Action::make('toggle_publish')
                    ->label(fn ($record) => $record->status === 'published' ? 'Unpublish' : 'Publish')
                    ->icon(fn ($record) => $record->status === 'published'
                        ? 'heroicon-o-eye-slash'
                        : 'heroicon-o-eye'
                    )
                    ->action(function ($record) {
                        if ($record->status === 'published') {
                            $record->update(['status' => 'draft']);
                        } else {
                            $record->update([
                                'status'       => 'published',
                                'published_at' => $record->published_at ?? now(),
                            ]);
                        }
                    })
                    ->requiresConfirmation(false),
                \Filament\Actions\DeleteAction::make(),
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
            'index'  => Pages\ListJobPositions::route('/'),
            'create' => Pages\CreateJobPosition::route('/create'),
            'edit'   => Pages\EditJobPosition::route('/{record}/edit'),
        ];
    }
}
