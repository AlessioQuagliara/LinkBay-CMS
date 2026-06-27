<?php

declare(strict_types=1);

namespace App\Http\Controllers\Tenant\Storefront;

use App\Http\Controllers\Controller;
use App\Models\Tenant\MediaFile;
use Illuminate\Http\JsonResponse;

class MediaController extends Controller
{
    public function show(int $id): JsonResponse
    {
        $media = MediaFile::findOrFail($id);

        return response()->json([
            'data' => [
                'id' => $media->id,
                'name' => $media->name,
                'file_name' => $media->file_name,
                'mime_type' => $media->mime_type,
                'size' => $media->size,
                'url' => $media->url(),
                'alt_text' => $media->alt_text,
                'title' => $media->title,
                'collection' => $media->collection,
            ],
        ]);
    }
}
