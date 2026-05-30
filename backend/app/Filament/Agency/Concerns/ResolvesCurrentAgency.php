<?php

declare(strict_types=1);

namespace App\Filament\Agency\Concerns;

use App\Models\Central\Agency;

trait ResolvesCurrentAgency
{
    protected function agency(): ?Agency
    {
        // Prova prima il binding del container (già risolto in register())
        if (app()->has('current_agency')) {
            $agency = app('current_agency');
            if ($agency instanceof Agency) {
                // Eager load plan se non ancora caricato
                if (!$agency->relationLoaded('plan')) {
                    $agency->load('plan');
                }
                return $agency;
            }
        }

        // Fallback: query diretta basata sull'host della request corrente
        try {
            $host   = request()->getHost();
            $agency = Agency::with('plan')
                ->where('custom_domain', $host)
                ->orWhere('slug', explode('.', $host)[0])
                ->first();

            // Aggiorna il binding per le chiamate successive nello stesso request
            app()->instance('current_agency', $agency);

            return $agency;
        } catch (\Throwable) {
            return null;
        }
    }
}
