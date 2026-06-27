<x-filament-widgets::widget>
    <x-filament::section>
        <div class="flex flex-wrap items-center gap-2">
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Periodo:</span>

            @foreach (['today' => 'Oggi', 'yesterday' => 'Ieri', '7' => '7 giorni', '30' => '30 giorni', 'this_month' => 'Questo mese', 'last_month' => 'Mese scorso', '90' => '90 giorni'] as $key => $label)
                <button
                    wire:click="applyPreset('{{ $key }}')"
                    class="rounded-md px-3 py-1 text-sm font-medium transition-colors
                        {{ $preset === $key
                            ? 'bg-primary-600 text-white shadow-sm'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200 dark:bg-gray-700 dark:text-gray-300 dark:hover:bg-gray-600' }}"
                >
                    {{ $label }}
                </button>
            @endforeach

            <div class="ml-auto flex items-center gap-2">
                <input
                    type="date"
                    wire:model="customFrom"
                    class="rounded-md border border-gray-300 px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-800 dark:text-white"
                />
                <span class="text-gray-500">—</span>
                <input
                    type="date"
                    wire:model="customTo"
                    class="rounded-md border border-gray-300 px-2 py-1 text-sm dark:border-gray-600 dark:bg-gray-800 dark:text-white"
                />
                <button
                    wire:click="applyCustom"
                    class="rounded-md bg-gray-800 px-3 py-1 text-sm font-medium text-white hover:bg-gray-700 dark:bg-gray-700 dark:hover:bg-gray-600"
                >
                    Applica
                </button>
            </div>
        </div>
    </x-filament::section>
</x-filament-widgets::widget>
