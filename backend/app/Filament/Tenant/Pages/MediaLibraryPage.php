<?php

declare(strict_types=1);

namespace App\Filament\Tenant\Pages;

use App\Models\Tenant\MediaFile;
use App\Services\Tenant\MediaService;
use Filament\Notifications\Notification;
use Filament\Pages\Page;
use Illuminate\Http\UploadedFile;

class MediaLibraryPage extends Page
{
    protected static string|\BackedEnum|null $navigationIcon = 'heroicon-o-photo';

    protected static string|\UnitEnum|null $navigationGroup = 'Marketing';

    protected static ?string $navigationLabel = 'Media';

    protected static ?int $navigationSort = 6;

    protected string $view = 'filament.tenant.pages.media-library';

    public string $activeCollection = '';

    public ?int $selectedMediaId = null;

    public string $editAltText = '';

    public string $editTitle = '';

    public function getMediaProperty()
    {
        $query = MediaFile::orderByDesc('created_at');

        if ($this->activeCollection !== '') {
            $query->forCollection($this->activeCollection);
        }

        return $query->paginate(24);
    }

    public function getCollectionsProperty(): array
    {
        return MediaFile::select('collection')
            ->distinct()
            ->whereNotNull('collection')
            ->pluck('collection')
            ->all();
    }

    public function getSelectedMediaProperty(): ?MediaFile
    {
        if (! $this->selectedMediaId) {
            return null;
        }

        return MediaFile::find($this->selectedMediaId);
    }

    public function upload(): void
    {
        // Handled via Livewire file upload in the blade
    }

    public function handleUpload(array $files, string $collection = 'general'): void
    {
        $service = app(MediaService::class);

        foreach ($files as $file) {
            if ($file instanceof UploadedFile) {
                $service->upload($file, $collection ?: 'general');
            }
        }

        Notification::make()->title('File caricati')->success()->send();
    }

    public function selectMedia(int $id): void
    {
        $media = MediaFile::findOrFail($id);
        $this->selectedMediaId = $id;
        $this->editAltText = $media->alt_text ?? '';
        $this->editTitle = $media->title ?? '';
    }

    public function updateMedia(): void
    {
        if (! $this->selectedMediaId) {
            return;
        }

        MediaFile::findOrFail($this->selectedMediaId)->update([
            'alt_text' => $this->editAltText,
            'title' => $this->editTitle,
        ]);

        Notification::make()->title('Media aggiornato')->success()->send();
        $this->closeModal();
    }

    public function deleteMedia(): void
    {
        if (! $this->selectedMediaId) {
            return;
        }

        $media = MediaFile::findOrFail($this->selectedMediaId);
        app(MediaService::class)->delete($media);

        Notification::make()->title('Media eliminato')->success()->send();
        $this->closeModal();
    }

    public function closeModal(): void
    {
        $this->selectedMediaId = null;
        $this->editAltText = '';
        $this->editTitle = '';
    }

    public function filterCollection(string $collection): void
    {
        $this->activeCollection = $collection;
        $this->resetPage();
    }

    protected function resetPage(): void
    {
        // Trigger Livewire pagination reset
        $this->dispatch('$refresh');
    }
}
