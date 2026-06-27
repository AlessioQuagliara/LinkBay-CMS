<?php

declare(strict_types=1);

namespace App\Services\Tenant;

use App\Models\Tenant\MediaFile;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Http\UploadedFile;
use Illuminate\Pagination\LengthAwarePaginator;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\Storage;

class MediaService
{
    public function upload(UploadedFile $file, string $collection, array $meta = []): MediaFile
    {
        $tenantId = $this->resolveTenantId();
        $dir = "tenants/{$tenantId}/media/{$collection}";
        $path = $file->store($dir, 'public');

        return MediaFile::create([
            'tenant_id' => $tenantId,
            'name' => $meta['name'] ?? pathinfo($file->getClientOriginalName(), PATHINFO_FILENAME),
            'file_name' => $file->getClientOriginalName(),
            'mime_type' => $file->getMimeType() ?? $file->getClientMimeType(),
            'disk' => 'public',
            'path' => $path,
            'size' => $file->getSize(),
            'alt_text' => $meta['alt_text'] ?? null,
            'title' => $meta['title'] ?? null,
            'collection' => $collection,
            'metadata' => $meta['metadata'] ?? null,
            'created_by' => Auth::id(),
        ]);
    }

    public function delete(MediaFile $media): void
    {
        if (Storage::disk($media->disk)->exists($media->path)) {
            Storage::disk($media->disk)->delete($media->path);
        }

        $media->delete();
    }

    public function getByCollection(string $collection, int $perPage = 24): LengthAwarePaginator
    {
        return MediaFile::forCollection($collection)
            ->orderByDesc('created_at')
            ->paginate($perPage);
    }

    public function attachToModel(MediaFile $media, Model $model, string $field): void
    {
        $model->update([$field => $media->url()]);
    }

    private function resolveTenantId(): string
    {
        try {
            if (function_exists('tenancy') && tenancy()->initialized) {
                return (string) tenant()->id;
            }
        } catch (\Throwable) {
        }

        return 'default';
    }
}
