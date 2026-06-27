<x-filament-panels::page>
    <div class="space-y-4">

        {{-- Breadcrumb / collection filter --}}
        <div class="flex flex-wrap items-center gap-2">
            <button
                type="button"
                wire:click="filterCollection('')"
                class="{{ $activeCollection === '' ? 'bg-primary-600 text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700' }} px-3 py-1 rounded-full text-sm font-medium transition"
            >
                Tutti
            </button>
            @foreach ($this->collections as $col)
                <button
                    type="button"
                    wire:click="filterCollection('{{ $col }}')"
                    class="{{ $activeCollection === $col ? 'bg-primary-600 text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-700' }} px-3 py-1 rounded-full text-sm font-medium transition capitalize"
                >
                    {{ $col }}
                </button>
            @endforeach
        </div>

        {{-- Upload area --}}
        <x-filament::section>
            <div
                x-data="{
                    dragging: false,
                    async handleDrop(e) {
                        this.dragging = false;
                        const files = [...e.dataTransfer.files];
                        await $wire.call('handleUpload', files, '{{ $activeCollection ?: 'general' }}');
                    },
                    async handleInput(e) {
                        const files = [...e.target.files];
                        await $wire.call('handleUpload', files, '{{ $activeCollection ?: 'general' }}');
                    }
                }"
                x-on:dragover.prevent="dragging = true"
                x-on:dragleave="dragging = false"
                x-on:drop.prevent="handleDrop($event)"
                :class="dragging ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' : 'border-gray-300 dark:border-gray-600'"
                class="border-2 border-dashed rounded-xl p-8 text-center cursor-pointer transition-colors"
                x-on:click="$refs.fileInput.click()"
            >
                <x-heroicon-o-cloud-arrow-up class="w-10 h-10 text-gray-400 mx-auto mb-2" />
                <p class="text-sm text-gray-600 dark:text-gray-400">
                    Trascina file qui o <span class="text-primary-600 underline">clicca per selezionare</span>
                </p>
                <p class="text-xs text-gray-400 mt-1">PNG, JPG, GIF, SVG, PDF — più file contemporaneamente</p>
                <input type="file" x-ref="fileInput" class="hidden" multiple x-on:change="handleInput($event)" />
            </div>
        </x-filament::section>

        {{-- Media grid --}}
        @if ($this->media->isEmpty())
            <div class="text-center py-12 text-gray-500 dark:text-gray-400">
                <x-heroicon-o-photo class="w-12 h-12 mx-auto mb-2 opacity-40" />
                <p>Nessun file caricato.</p>
            </div>
        @else
            <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
                @foreach ($this->media as $item)
                    <button
                        type="button"
                        wire:click="selectMedia({{ $item->id }})"
                        class="group relative aspect-square rounded-lg overflow-hidden border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800 hover:ring-2 hover:ring-primary-500 transition"
                    >
                        @if ($item->isImage())
                            <img
                                src="{{ $item->url() }}"
                                alt="{{ $item->alt_text ?? $item->name }}"
                                class="w-full h-full object-cover"
                                loading="lazy"
                            />
                        @else
                            <div class="flex items-center justify-center w-full h-full">
                                <x-heroicon-o-document class="w-8 h-8 text-gray-400" />
                            </div>
                        @endif
                        <div class="absolute inset-0 bg-black/0 group-hover:bg-black/30 transition flex items-end p-1 opacity-0 group-hover:opacity-100">
                            <p class="text-white text-xs truncate w-full">{{ $item->name }}</p>
                        </div>
                    </button>
                @endforeach
            </div>

            <div class="mt-4">
                {{ $this->media->links() }}
            </div>
        @endif
    </div>

    {{-- Media detail modal --}}
    @if ($selectedMediaId && $this->selectedMedia)
        @php $media = $this->selectedMedia; @endphp
        <div
            class="fixed inset-0 z-50 flex items-center justify-center bg-black/60 p-4"
            wire:click.self="closeModal"
        >
            <div class="bg-white dark:bg-gray-900 rounded-xl shadow-2xl w-full max-w-lg">
                <div class="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
                    <h2 class="font-semibold text-gray-900 dark:text-white truncate">{{ $media->name }}</h2>
                    <button type="button" wire:click="closeModal" class="text-gray-400 hover:text-gray-600">
                        <x-heroicon-o-x-mark class="w-5 h-5" />
                    </button>
                </div>

                <div class="p-4 space-y-4">
                    @if ($media->isImage())
                        <img
                            src="{{ $media->url() }}"
                            alt="{{ $media->alt_text }}"
                            class="w-full max-h-64 object-contain rounded-lg bg-gray-50 dark:bg-gray-800"
                        />
                    @endif

                    <div class="text-xs text-gray-500 space-y-1">
                        <p>File: <span class="font-mono">{{ $media->file_name }}</span></p>
                        <p>Dimensione: {{ number_format($media->size / 1024, 1) }} KB</p>
                        <p>Collection: <span class="capitalize">{{ $media->collection ?? '—' }}</span></p>
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Testo alternativo</label>
                        <input
                            type="text"
                            wire:model="editAltText"
                            class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm px-3 py-2"
                            placeholder="Descrivi l'immagine…"
                        />
                    </div>

                    <div>
                        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Titolo</label>
                        <input
                            type="text"
                            wire:model="editTitle"
                            class="w-full rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm px-3 py-2"
                        />
                    </div>

                    <div class="text-xs text-gray-500">
                        <p class="mb-1">URL:</p>
                        <div class="flex gap-2">
                            <input
                                type="text"
                                value="{{ $media->url() }}"
                                readonly
                                class="flex-1 font-mono rounded-lg border border-gray-300 dark:border-gray-600 bg-gray-50 dark:bg-gray-800 text-xs px-3 py-1"
                                x-ref="urlInput{{ $media->id }}"
                            />
                            <button
                                type="button"
                                x-on:click="navigator.clipboard.writeText('{{ $media->url() }}'); $dispatch('filament-notification', { title: 'URL copiato', status: 'success' })"
                                class="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded-lg hover:bg-gray-200 text-gray-600 dark:text-gray-300"
                                title="Copia URL"
                            >
                                <x-heroicon-o-clipboard class="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                </div>

                <div class="flex items-center justify-between p-4 border-t border-gray-200 dark:border-gray-700">
                    <x-filament::button color="danger" wire:click="deleteMedia" wire:confirm="Eliminare questo file?">
                        Elimina
                    </x-filament::button>
                    <x-filament::button color="primary" wire:click="updateMedia">
                        Salva modifiche
                    </x-filament::button>
                </div>
            </div>
        </div>
    @endif
</x-filament-panels::page>
