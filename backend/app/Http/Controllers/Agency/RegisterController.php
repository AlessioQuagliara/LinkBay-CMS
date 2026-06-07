<?php

declare(strict_types=1);

namespace App\Http\Controllers\Agency;

use App\Http\Controllers\Controller;
use App\Models\Central\Agency;
use App\Models\Central\AgencyMember;
use App\Models\Central\User;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
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
            'slug' => ['required', 'string', 'max:63', 'regex:/^[a-z0-9][a-z0-9-]*[a-z0-9]$/', Rule::unique(Agency::class, 'slug')],
            'email' => ['required', 'email', Rule::unique(User::class, 'email')],
            'password' => ['required', 'string', 'min:8', 'confirmed'],
        ], [
            'slug.regex' => 'Lo slug può contenere solo lettere minuscole, numeri e trattini, e non può iniziare/terminare con un trattino.',
            'slug.unique' => 'Questo sottodominio è già in uso.',
            'email.unique' => 'Questa email è già registrata.',
        ]);

        // Auto-approva in local, pending in produzione
        $status = app()->isLocal() ? 'active' : 'pending';

        $agency = Agency::create([
            'name' => $validated['agency_name'],
            'slug' => $validated['slug'],
            'brand_name' => $validated['agency_name'],
            'status' => $status,
            'billing_type' => 'monthly',
        ]);

        $user = User::create([
            'name' => $validated['agency_name'],
            'email' => $validated['email'],
            'password' => Hash::make($validated['password']),
            'is_super_admin' => false,
        ]);

        $agency->update(['owner_user_id' => $user->id]);

        AgencyMember::create([
            'agency_id' => $agency->id,
            'user_id' => $user->id,
            'role' => AgencyMember::ROLE_OWNER,
            'status' => AgencyMember::STATUS_ACTIVE,
            'accepted_at' => now(),
        ]);

        $agencyDomain = $validated['slug'].'.'.config('app.central_domain', 'linkbay-cms.test');

        if ($status === 'active') {
            // Derive scheme from APP_URL so HTTP local and HTTPS prod both work.
            $scheme = parse_url(config('app.url'), PHP_URL_SCHEME) ?? 'http';
            $loginUrl = $scheme.'://'.$agencyDomain.'/dashboard/login';

            return redirect($loginUrl)->with(
                'success',
                'Account creato! Login alla tua dashboard.'
            );
        }

        return redirect(route('agency.register'))
            ->with('success', 'Registrazione completata! Il tuo account è in fase di approvazione. Riceverai una email a breve.');
    }
}
