<x-filament-panels::page>
    <div class="space-y-6">
        <x-filament-panels::form wire:submit="save">
            {{ $this->form }}

            <div class="flex items-center gap-3 mt-4">
                <x-filament::button type="submit" color="primary">
                    Salva brand
                </x-filament::button>

                <x-filament::button type="button" color="gray" wire:click="previewCss">
                    Anteprima stile CSS
                </x-filament::button>
            </div>
        </x-filament-panels::form>
    </div>

    <div
        x-data="{ open: false, css: '' }"
        x-on:open-css-preview.window="open = true; css = $event.detail.css"
        x-show="open"
        x-cloak
        class="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
    >
        <div class="bg-white dark:bg-gray-900 rounded-xl shadow-2xl w-full max-w-2xl mx-4 p-6">
            <div class="flex items-center justify-between mb-4">
                <h2 class="text-lg font-semibold text-gray-900 dark:text-white">Anteprima variabili CSS</h2>
                <button type="button" x-on:click="open = false" class="text-gray-400 hover:text-gray-600">
                    <x-heroicon-o-x-mark class="w-5 h-5" />
                </button>
            </div>
            <pre
                class="bg-gray-100 dark:bg-gray-800 text-sm font-mono p-4 rounded-lg overflow-auto max-h-96 text-gray-800 dark:text-gray-200"
                x-text="css"
            ></pre>
        </div>
    </div>
</x-filament-panels::page>
