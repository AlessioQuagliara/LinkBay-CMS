<?php

declare(strict_types=1);

namespace App\Services;

use App\Models\Central\Agency;

/**
 * Centralised registry of premium pack metadata.
 *
 * Single source of truth for pack labels, descriptions, and included assets.
 * Used by upgrade-nudge widgets, MyEntitlementsPage, and AgencyBillingPage so
 * copy is never duplicated across view files.
 */
class PremiumPackConfig
{
    /**
     * @return array<int, array{
     *   featureCode: string,
     *   label: string,
     *   description: string,
     *   type: string,
     *   includes: string[],
     *   ctaLabel: string,
     * }>
     */
    public static function all(): array
    {
        return [
            [
                'featureCode' => 'theme_pack_editorial',
                'label' => 'Theme Pack Editorial',
                'description' => 'Temi per brand con un\'identità visiva forte e ricercata: dark mode, tipografia editoriale, palette sofisticate. Ideale per fashion, luxury e istituzioni culturali.',
                'type' => 'theme_pack',
                'includes' => ['Midnight', 'Noir'],
                'ctaLabel' => 'Richiedi attivazione',
            ],
            [
                'featureCode' => 'theme_pack_business',
                'label' => 'Theme Pack Business',
                'description' => 'Temi professionali per contesti business e creativi: caldi e artigianali o precisi e corporate. Pensati per studi, consulenze, SaaS e fintech.',
                'type' => 'theme_pack',
                'includes' => ['Atelier', 'Meridian'],
                'ctaLabel' => 'Richiedi attivazione',
            ],
            [
                'featureCode' => 'block_pack_marketing',
                'label' => 'Marketing Block Pack',
                'description' => 'Blocchi premium per landing page ad alta conversione. Aggiungono sezioni strutturate e pronte all\'uso nel Builder dei template.',
                'type' => 'block_pack',
                'includes' => ['Pricing Table', 'Logo Cloud', 'Stats Strip', 'Testimonial Carousel', 'CTA Split'],
                'ctaLabel' => 'Richiedi attivazione',
            ],
        ];
    }

    /**
     * Returns the pack definition for a given feature code, or null if not found.
     *
     * @return array{featureCode: string, label: string, description: string, type: string, includes: string[], ctaLabel: string}|null
     */
    public static function forCode(string $featureCode): ?array
    {
        foreach (static::all() as $pack) {
            if ($pack['featureCode'] === $featureCode) {
                return $pack;
            }
        }

        return null;
    }

    /**
     * Returns packs the agency does NOT currently have access to.
     * When $agency is null, returns all packs (safe default for unauthenticated contexts).
     *
     * @return array<int, array{featureCode: string, label: string, description: string, type: string, includes: string[], ctaLabel: string}>
     */
    public static function unavailableFor(?Agency $agency): array
    {
        if ($agency === null) {
            return static::all();
        }

        $service = app(FeatureAccessService::class);

        return array_values(array_filter(
            static::all(),
            fn (array $pack): bool => ! $service->canUseFeature($agency, $pack['featureCode']),
        ));
    }
}
