<?php

declare(strict_types=1);

namespace Database\Seeders;

use App\Models\Central\ThemePreset;
use App\Services\ThemeConfigSchema;
use Illuminate\Database\Seeder;

class ThemePresetSeeder extends Seeder
{
    public function run(): void
    {
        foreach (ThemeConfigSchema::systemPresets() as $preset) {
            ThemePreset::firstOrCreate(
                ['slug' => $preset['slug'], 'is_system' => true],
                [
                    'agency_id' => null,
                    'name' => $preset['name'],
                    'slug' => $preset['slug'],
                    'status' => ThemePreset::STATUS_ACTIVE,
                    'is_system' => true,
                    'config' => ThemeConfigSchema::normalize($preset['config']),
                ],
            );
        }

        $this->command->info('ThemePresetSeeder: '.count(ThemeConfigSchema::systemPresets()).' system presets creati/aggiornati.');
    }
}
