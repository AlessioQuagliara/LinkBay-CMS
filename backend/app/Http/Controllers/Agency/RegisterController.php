<?php

declare(strict_types=1);

namespace App\Http\Controllers\Agency;

use App\Http\Controllers\Controller;
use App\Mail\AgencyWelcomeMail;
use App\Models\Central\Agency;
use App\Models\Central\AgencyMember;
use App\Models\Central\User;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Mail;
use Illuminate\Support\Str;
use Illuminate\Validation\Rule;
use Illuminate\View\View;

class RegisterController extends Controller
{
    public function show(): View
    {
        return view('agency.auth.register');
    }

    public function store(Request $request): RedirectResponse
    {
        $validated = $request->validate([
            'agency_name' => ['required', 'string', 'max:255'],
            'slug'        => ['nullable', 'string', 'max:63', 'regex:/^[a-z0-9][a-z0-9-]*[a-z0-9]$/'],
            'email'       => ['required', 'email', Rule::unique(User::class, 'email')],
            'password'    => ['required', 'string', 'min:8', 'confirmed'],
        ], [
            'slug.regex'   => 'Lo slug può contenere solo lettere minuscole, numeri e trattini, e non può iniziare/terminare con un trattino.',
            'email.unique' => 'Questa email è già registrata.',
        ]);

        // ── Slug: usa quello fornito oppure generalo dal nome agenzia ──────────
        $slug = $this->resolveUniqueSlug(
            $validated['slug'] ?? Str::slug($validated['agency_name'])
        );

        // Verifica unicità slug dopo la risoluzione
        if (Agency::where('slug', $slug)->exists() && empty($validated['slug'])) {
            // resolveUniqueSlug ha già gestito questo caso, ma per sicurezza:
            $slug = $this->resolveUniqueSlug($slug);
        }

        // Blocca esplicitamente se lo slug fornito manualmente è già in uso
        if (! empty($validated['slug']) && Agency::where('slug', $validated['slug'])->exists()) {
            return back()
                ->withInput()
                ->withErrors(['slug' => 'Questo sottodominio è già in uso.']);
        }

        // ── Stato: auto-approva in local, pending in produzione ───────────────
        $status = app()->isLocal() ? 'active' : 'pending';

        $agency = Agency::create([
            'name'         => $validated['agency_name'],
            'slug'         => $slug,
            'brand_name'   => $validated['agency_name'],
            'status'       => $status,
            'billing_type' => 'monthly',
        ]);

        $user = User::create([
            'name'           => $validated['agency_name'],
            'email'          => $validated['email'],
            'password'       => Hash::make($validated['password']),
            'is_super_admin' => false,
        ]);

        $agency->update(['owner_user_id' => $user->id]);

        AgencyMember::create([
            'agency_id'   => $agency->id,
            'user_id'     => $user->id,
            'role'        => AgencyMember::ROLE_OWNER,
            'status'      => AgencyMember::STATUS_ACTIVE,
            'accepted_at' => now(),
        ]);

        // ── Welcome email ─────────────────────────────────────────────────────
        $agencyDomain = $slug . '.' . config('app.central_domain', 'linkbay-cms.test');
        $scheme       = parse_url(config('app.url'), PHP_URL_SCHEME) ?? 'http';
        $loginUrl     = $scheme . '://' . $agencyDomain . '/dashboard/login';

        Mail::to($user->email)->send(new AgencyWelcomeMail($agency, $user, $loginUrl));

        // ── Redirect ──────────────────────────────────────────────────────────
        if ($status === 'active') {
            return redirect($loginUrl)->with(
                'success',
                'Account creato! Login alla tua dashboard.'
            );
        }

        return redirect(route('agency.register'))
            ->with('success', 'Registrazione completata! Il tuo account è in fase di approvazione. Riceverai una email a breve.');
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    /**
     * Genera uno slug unico aggiungendo un suffisso numerico incrementale
     * nel caso in cui lo slug base sia già occupato.
     *
     * Esempi: 'my-agency' → 'my-agency-2' → 'my-agency-3' …
     */
    private function resolveUniqueSlug(string $base): string
    {
        $slug    = $base;
        $counter = 2;

        while (Agency::where('slug', $slug)->exists()) {
            $slug = $base . '-' . $counter;
            $counter++;
        }

        return $slug;
    }
}
