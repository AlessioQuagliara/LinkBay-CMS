<?php

declare(strict_types=1);

namespace App\Plugins\MarketingBlockPack;

use App\Plugins\BlockDefinition;
use App\Plugins\PluginRegistry;
use Filament\Forms\Components\Repeater;
use Filament\Forms\Components\Select;
use Filament\Forms\Components\Textarea;
use Filament\Forms\Components\TextInput;
use Filament\Forms\Components\Toggle;
use Illuminate\Support\ServiceProvider;

/**
 * Registers the Marketing Block Pack premium blocks into the PluginRegistry.
 *
 * Feature code: block_pack_marketing
 * All blocks require an active AgencyEntitlement for this code.
 *
 * Blocks registered: pricing_table, logo_cloud, stats_strip, testimonial_carousel, cta_split.
 *
 * Loaded automatically by PluginServiceProvider.
 * To enable for an agency: Admin → Marketplace → Entitlements → grant block_pack_marketing.
 */
class MarketingBlockPackServiceProvider extends ServiceProvider
{
    public const FEATURE_CODE = 'block_pack_marketing';

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
                key: 'pricing_table',
                label: 'Pricing Table',
                fieldsBuilder: static fn (): array => [
                    TextInput::make('section_title')->label('Titolo sezione')->maxLength(200),
                    TextInput::make('section_subtitle')->label('Sottotitolo')->maxLength(300),
                    Select::make('columns')
                        ->label('Colonne')
                        ->options(['2' => '2', '3' => '3', '4' => '4'])
                        ->default('3'),
                    Repeater::make('tiers')
                        ->label('Piani')
                        ->schema([
                            TextInput::make('name')->label('Nome piano')->required()->maxLength(80),
                            TextInput::make('price')->label('Prezzo')->maxLength(40),
                            TextInput::make('period')->label('Periodo (es. /mese)')->maxLength(40),
                            Textarea::make('description')->label('Descrizione breve')->rows(2)->maxLength(300),
                            Toggle::make('is_featured')->label('In evidenza'),
                            TextInput::make('cta_label')->label('Testo CTA')->maxLength(80),
                            TextInput::make('cta_url')->label('URL CTA')->url()->maxLength(500),
                            Repeater::make('features')
                                ->label('Feature incluse')
                                ->schema([
                                    TextInput::make('text')->label('Feature')->required()->maxLength(150),
                                    Toggle::make('included')->label('Inclusa')->default(true),
                                ])
                                ->addActionLabel('Aggiungi feature')
                                ->maxItems(12)
                                ->collapsible(),
                        ])
                        ->addActionLabel('Aggiungi piano')
                        ->minItems(1)
                        ->maxItems(4)
                        ->reorderableWithButtons()
                        ->collapsible(),
                ],
                icon: 'heroicon-o-currency-euro',
                featureCode: self::FEATURE_CODE,
            ),

            new BlockDefinition(
                key: 'logo_cloud',
                label: 'Logo Cloud',
                fieldsBuilder: static fn (): array => [
                    TextInput::make('title')->label('Titolo')->maxLength(200),
                    TextInput::make('subtitle')->label('Sottotitolo')->maxLength(300),
                    Select::make('columns')
                        ->label('Colonne')
                        ->options(['3' => '3', '4' => '4', '5' => '5', '6' => '6'])
                        ->default('4'),
                    Repeater::make('logos')
                        ->label('Loghi')
                        ->schema([
                            TextInput::make('name')->label('Nome brand')->required()->maxLength(100),
                            TextInput::make('image_url')->label('URL immagine')->url()->required()->maxLength(500),
                            TextInput::make('link_url')->label('URL link (opzionale)')->url()->maxLength(500),
                        ])
                        ->addActionLabel('Aggiungi logo')
                        ->minItems(1)
                        ->maxItems(20)
                        ->reorderableWithButtons()
                        ->collapsible(),
                ],
                icon: 'heroicon-o-squares-2x2',
                featureCode: self::FEATURE_CODE,
            ),

            new BlockDefinition(
                key: 'stats_strip',
                label: 'Stats Strip',
                fieldsBuilder: static fn (): array => [
                    TextInput::make('title')->label('Titolo (opzionale)')->maxLength(200),
                    Select::make('background')
                        ->label('Sfondo')
                        ->options([
                            'light' => 'Chiaro',
                            'dark' => 'Scuro',
                            'brand' => 'Brand color',
                        ])
                        ->default('light'),
                    Repeater::make('stats')
                        ->label('Statistiche')
                        ->schema([
                            TextInput::make('value')->label('Valore (es. 12.000+)')->required()->maxLength(50),
                            TextInput::make('label')->label('Etichetta')->required()->maxLength(100),
                            TextInput::make('description')->label('Descrizione breve')->maxLength(200),
                            TextInput::make('icon')->label('Icona heroicon (opzionale)')->maxLength(80),
                        ])
                        ->addActionLabel('Aggiungi stat')
                        ->minItems(1)
                        ->maxItems(6)
                        ->columns(2)
                        ->reorderableWithButtons()
                        ->collapsible(),
                ],
                icon: 'heroicon-o-chart-bar',
                featureCode: self::FEATURE_CODE,
            ),

            new BlockDefinition(
                key: 'testimonial_carousel',
                label: 'Testimonial Carousel',
                fieldsBuilder: static fn (): array => [
                    TextInput::make('section_title')->label('Titolo sezione')->maxLength(200),
                    Repeater::make('items')
                        ->label('Testimonianze')
                        ->schema([
                            Textarea::make('quote')->label('Citazione')->required()->rows(3)->maxLength(800),
                            TextInput::make('author')->label('Autore')->required()->maxLength(100),
                            TextInput::make('role')->label('Ruolo / Azienda')->maxLength(100),
                            TextInput::make('company')->label('Azienda')->maxLength(100),
                            TextInput::make('avatar_url')->label('URL avatar')->url()->maxLength(500),
                            Select::make('rating')
                                ->label('Rating')
                                ->options(['1' => '1★', '2' => '2★', '3' => '3★', '4' => '4★', '5' => '5★'])
                                ->default('5'),
                        ])
                        ->addActionLabel('Aggiungi testimonianza')
                        ->minItems(1)
                        ->maxItems(12)
                        ->reorderableWithButtons()
                        ->collapsible(),
                ],
                icon: 'heroicon-o-chat-bubble-left-ellipsis',
                featureCode: self::FEATURE_CODE,
            ),

            new BlockDefinition(
                key: 'cta_split',
                label: 'CTA Split',
                fieldsBuilder: static fn (): array => [
                    TextInput::make('eyebrow')->label('Eyebrow')->maxLength(100),
                    TextInput::make('title')->label('Titolo')->required()->maxLength(200),
                    Textarea::make('body')->label('Corpo testo')->rows(4)->maxLength(800),
                    TextInput::make('primary_cta_label')->label('CTA primaria — testo')->maxLength(80),
                    TextInput::make('primary_cta_url')->label('CTA primaria — URL')->url()->maxLength(500),
                    TextInput::make('secondary_cta_label')->label('CTA secondaria — testo')->maxLength(80),
                    TextInput::make('secondary_cta_url')->label('CTA secondaria — URL')->url()->maxLength(500),
                    TextInput::make('image_url')->label('URL immagine')->url()->maxLength(500),
                    Select::make('image_position')
                        ->label('Posizione immagine')
                        ->options(['left' => 'Sinistra', 'right' => 'Destra'])
                        ->default('right'),
                    Select::make('background')
                        ->label('Sfondo')
                        ->options([
                            'light' => 'Chiaro',
                            'dark' => 'Scuro',
                            'brand' => 'Brand color',
                        ])
                        ->default('light'),
                ],
                icon: 'heroicon-o-arrow-top-right-on-square',
                columns: 2,
                featureCode: self::FEATURE_CODE,
            ),
        ];
    }
}
