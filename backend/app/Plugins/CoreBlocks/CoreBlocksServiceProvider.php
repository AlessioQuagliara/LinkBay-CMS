<?php

declare(strict_types=1);

namespace App\Plugins\CoreBlocks;

use App\Plugins\BlockDefinition;
use App\Plugins\PluginRegistry;
use Filament\Forms\Components\Builder\Block;
use Filament\Forms\Components\Repeater;
use Filament\Forms\Components\Select;
use Filament\Forms\Components\Textarea;
use Filament\Forms\Components\TextInput;
use Illuminate\Support\ServiceProvider;

/**
 * Registers the 7 built-in v1 blocks into the PluginRegistry.
 *
 * Loaded automatically by PluginServiceProvider.
 * To add a premium block pack, create a separate service provider and
 * append it to PluginServiceProvider::$pluginProviders.
 *
 * Block keys registered: hero, feature_grid, rich_text, cta, faq, testimonial, spacer.
 */
class CoreBlocksServiceProvider extends ServiceProvider
{
    public function boot(): void
    {
        $registry = $this->app->make(PluginRegistry::class);

        foreach ($this->blockDefinitions() as $definition) {
            $registry->registerBlock($definition->key, $definition);
        }
    }

    /** @return BlockDefinition[] */
    private function blockDefinitions(): array
    {
        return [
            new BlockDefinition(
                key: 'hero',
                label: 'Hero',
                fieldsBuilder: static fn (): array => [
                    TextInput::make('eyebrow')->label('Eyebrow')->maxLength(100),
                    TextInput::make('title')->label('Titolo')->required()->maxLength(200),
                    Textarea::make('subtitle')->label('Sottotitolo')->rows(2)->maxLength(500),
                    TextInput::make('primary_cta_label')->label('CTA primaria — testo')->maxLength(80),
                    TextInput::make('primary_cta_url')->label('CTA primaria — URL')->url()->maxLength(500),
                    TextInput::make('secondary_cta_label')->label('CTA secondaria — testo')->maxLength(80),
                    TextInput::make('secondary_cta_url')->label('CTA secondaria — URL')->url()->maxLength(500),
                ],
                icon: 'heroicon-o-rocket-launch',
                columns: 2,
            ),

            new BlockDefinition(
                key: 'feature_grid',
                label: 'Feature Grid',
                fieldsBuilder: static fn (): array => [
                    TextInput::make('section_title')->label('Titolo sezione')->maxLength(200),
                    Repeater::make('items')
                        ->label('Feature')
                        ->schema([
                            TextInput::make('title')->label('Titolo')->required()->maxLength(100),
                            Textarea::make('description')->label('Descrizione')->rows(2)->maxLength(300),
                            TextInput::make('icon')->label('Icona (es: heroicon-o-star)')->maxLength(80),
                        ])
                        ->columns(2)
                        ->addActionLabel('Aggiungi feature')
                        ->minItems(1)
                        ->maxItems(6)
                        ->reorderableWithButtons()
                        ->collapsible(),
                ],
                icon: 'heroicon-o-squares-2x2',
            ),

            new BlockDefinition(
                key: 'rich_text',
                label: 'Testo Ricco',
                fieldsBuilder: static fn (): array => [
                    TextInput::make('title')->label('Titolo sezione')->maxLength(200),
                    Textarea::make('content')
                        ->label('Contenuto (Markdown)')
                        ->required()
                        ->rows(8)
                        ->maxLength(10000)
                        ->helperText('Sintassi Markdown — il contenuto viene convertito in HTML sicuro lato storefront.'),
                ],
                icon: 'heroicon-o-document-text',
            ),

            new BlockDefinition(
                key: 'cta',
                label: 'Call to Action',
                fieldsBuilder: static fn (): array => [
                    TextInput::make('title')->label('Titolo')->required()->maxLength(200),
                    Textarea::make('text')->label('Testo')->rows(3)->maxLength(500),
                    TextInput::make('button_label')->label('Testo pulsante')->maxLength(80),
                    TextInput::make('button_url')->label('URL pulsante')->url()->maxLength(500),
                ],
                icon: 'heroicon-o-cursor-arrow-rays',
                columns: 2,
            ),

            new BlockDefinition(
                key: 'faq',
                label: 'FAQ',
                fieldsBuilder: static fn (): array => [
                    TextInput::make('section_title')->label('Titolo sezione')->maxLength(200),
                    Repeater::make('items')
                        ->label('Domande')
                        ->schema([
                            TextInput::make('question')->label('Domanda')->required()->maxLength(300),
                            Textarea::make('answer')->label('Risposta')->required()->rows(3)->maxLength(1000),
                        ])
                        ->addActionLabel('Aggiungi FAQ')
                        ->minItems(1)
                        ->maxItems(20)
                        ->reorderableWithButtons()
                        ->collapsible(),
                ],
                icon: 'heroicon-o-question-mark-circle',
            ),

            new BlockDefinition(
                key: 'testimonial',
                label: 'Testimonianza',
                fieldsBuilder: static fn (): array => [
                    Textarea::make('quote')->label('Citazione')->required()->rows(4)->maxLength(1000),
                    TextInput::make('author')->label('Autore')->required()->maxLength(100),
                    TextInput::make('role')->label('Ruolo / Azienda')->maxLength(100),
                    TextInput::make('avatar_url')->label('URL avatar')->url()->maxLength(500),
                ],
                icon: 'heroicon-o-chat-bubble-left-right',
                columns: 2,
            ),

            new BlockDefinition(
                key: 'spacer',
                label: 'Spaziatore',
                fieldsBuilder: static fn (): array => [
                    Select::make('size')
                        ->label('Dimensione')
                        ->options([
                            'sm' => 'Piccolo (2rem)',
                            'md' => 'Medio (4rem)',
                            'lg' => 'Grande (6rem)',
                            'xl' => 'Extra Large (8rem)',
                        ])
                        ->default('md')
                        ->required(),
                ],
                icon: 'heroicon-o-arrows-up-down',
            ),
        ];
    }
}
