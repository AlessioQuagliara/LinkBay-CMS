<x-filament-panels::page>
    <div class="space-y-6">
        {{-- Current languages table --}}
        <x-filament::section heading="Lingue attive">
            @if (count($languages) === 0)
                <p class="text-sm text-gray-500 dark:text-gray-400">Nessuna lingua configurata. Aggiungine una qui sotto.</p>
            @else
                <div class="overflow-x-auto">
                    <table class="w-full text-sm">
                        <thead>
                            <tr class="text-left text-gray-500 dark:text-gray-400 border-b border-gray-200 dark:border-gray-700">
                                <th class="pb-2 pr-4">Lingua</th>
                                <th class="pb-2 pr-4">Locale</th>
                                <th class="pb-2 pr-4">Predefinita</th>
                                <th class="pb-2 pr-4">Attiva</th>
                                <th class="pb-2"></th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
                            @php $localeNames = \App\Filament\Tenant\Pages\LanguageSettingsPage::availableLocales(); @endphp
                            @foreach ($languages as $lang)
                                <tr class="py-2">
                                    <td class="py-2 pr-4 font-medium text-gray-900 dark:text-white">
                                        {{ $localeNames[$lang['locale']] ?? $lang['locale'] }}
                                    </td>
                                    <td class="py-2 pr-4 font-mono text-gray-500">{{ $lang['locale'] }}</td>
                                    <td class="py-2 pr-4">
                                        @if ($lang['is_default'])
                                            <x-filament::badge color="success">Predefinita</x-filament::badge>
                                        @else
                                            <x-filament::button
                                                size="xs"
                                                color="gray"
                                                wire:click="setDefault({{ $lang['id'] }})"
                                            >
                                                Imposta
                                            </x-filament::button>
                                        @endif
                                    </td>
                                    <td class="py-2 pr-4">
                                        <button
                                            type="button"
                                            wire:click="toggleActive({{ $lang['id'] }})"
                                            class="{{ $lang['is_active'] ? 'bg-primary-600' : 'bg-gray-200 dark:bg-gray-700' }} relative inline-flex h-5 w-9 items-center rounded-full transition-colors"
                                        >
                                            <span class="{{ $lang['is_active'] ? 'translate-x-5' : 'translate-x-1' }} inline-block h-3 w-3 transform rounded-full bg-white transition-transform"></span>
                                        </button>
                                    </td>
                                    <td class="py-2">
                                        @if (! $lang['is_default'])
                                            <x-filament::button
                                                size="xs"
                                                color="danger"
                                                wire:click="removeLanguage({{ $lang['id'] }})"
                                                wire:confirm="Rimuovere la lingua '{{ $lang['locale'] }}'?"
                                            >
                                                Rimuovi
                                            </x-filament::button>
                                        @endif
                                    </td>
                                </tr>
                            @endforeach
                        </tbody>
                    </table>
                </div>
            @endif
        </x-filament::section>

        {{-- Add language --}}
        <x-filament::section heading="Aggiungi lingua">
            <form wire:submit="addLanguage" class="flex items-end gap-4 flex-wrap">
                <div class="flex-1 min-w-48">
                    <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Lingua</label>
                    <select
                        wire:model="newLocale"
                        class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm px-3 py-2"
                    >
                        <option value="">Seleziona una lingua…</option>
                        @foreach (\App\Filament\Tenant\Pages\LanguageSettingsPage::availableLocales() as $code => $name)
                            <option value="{{ $code }}">{{ $name }} ({{ $code }})</option>
                        @endforeach
                    </select>
                    @error('newLocale') <p class="mt-1 text-xs text-danger-600">{{ $message }}</p> @enderror
                </div>

                <div class="flex items-center gap-2 mb-1">
                    <input
                        type="checkbox"
                        id="newIsActive"
                        wire:model="newIsActive"
                        class="rounded border-gray-300"
                    />
                    <label for="newIsActive" class="text-sm text-gray-700 dark:text-gray-300">Attiva subito</label>
                </div>

                <x-filament::button type="submit" color="primary">
                    Aggiungi
                </x-filament::button>
            </form>
        </x-filament::section>
    </div>
</x-filament-panels::page>
