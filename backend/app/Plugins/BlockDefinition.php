<?php

declare(strict_types=1);

namespace App\Plugins;

use Filament\Forms\Components\Builder\Block;
use Filament\Forms\Components\Field;

/**
 * Immutable descriptor for a single layout block type.
 *
 * Separates block metadata (key, label, icon — used for whitelisting and UI)
 * from the Filament schema (only built lazily when a form is rendered).
 *
 * To register a new block:
 *   $registry->registerBlock('my_block', new BlockDefinition(
 *       key: 'my_block',
 *       label: 'My Block',
 *       fieldsBuilder: static fn () => [
 *           TextInput::make('title')->required(),
 *       ],
 *   ));
 *
 * Optional parameters (icon, category, columns) come last so PHP defaults
 * are reachable with positional arguments as well as named arguments.
 *
 * @param  string  $key  Unique identifier used by the renderer whitelist
 * @param  string  $label  Human-readable label shown in the Builder UI
 * @param  \Closure(): array<Field>  $fieldsBuilder  Returns the block's form fields
 * @param  string  $icon  Heroicon name for the block picker
 * @param  string|null  $category  Optional grouping key (used in v2 block library)
 * @param  int  $columns  Number of columns for the block's form grid
 * @param  string|null  $featureCode  PluginCatalogItem code required to use this block (null = free)
 */
class BlockDefinition
{
    public function __construct(
        public readonly string $key,
        public readonly string $label,
        private readonly \Closure $fieldsBuilder,
        public readonly string $icon = 'heroicon-o-cube',
        public readonly ?string $category = null,
        public readonly int $columns = 1,
        public readonly ?string $featureCode = null,
    ) {}

    /**
     * Builds the Filament Builder Block for use in panel form schemas.
     * The closure is evaluated lazily — only when a form is rendered.
     */
    public function toFilamentBlock(): Block
    {
        $block = Block::make($this->key)
            ->label($this->label)
            ->icon($this->icon)
            ->schema(($this->fieldsBuilder)());

        if ($this->columns > 1) {
            $block->columns($this->columns);
        }

        return $block;
    }
}
