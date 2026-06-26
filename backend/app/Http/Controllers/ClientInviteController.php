<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Services\ClientInviteService;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;

class ClientInviteController extends Controller
{
    public function __construct(private readonly ClientInviteService $inviteService) {}

    /**
     * Show the invite acceptance form.
     */
    public function show(string $token): View|RedirectResponse
    {
        $contact = $this->inviteService->findByToken($token);

        if (! $contact) {
            return redirect()->route('client-invite.invalid');
        }

        if ($contact->isInviteExpired()) {
            return redirect()->route('client-invite.invalid')->with('reason', 'expired');
        }

        try {
            $storeName = $contact->inviteTenant?->name ?? '—';
        } catch (\Throwable) {
            $storeName = '—';
        }

        return view('client-invite.show', [
            'contact'   => $contact,
            'storeName' => $storeName,
            'token'     => $token,
        ]);
    }

    /**
     * Accept the invite: provision TenantUser and redirect to the store.
     */
    public function accept(Request $request, string $token): RedirectResponse
    {
        $contact = $this->inviteService->findByToken($token);

        if (! $contact || $contact->isInviteExpired()) {
            return redirect()->route('client-invite.invalid')->with('reason', 'expired');
        }

        // ── Cross-agency guard ────────────────────────────────────────────────
        // Se l'utente è autenticato, il contatto deve appartenere alla sua agenzia.
        // Questo previene che un membro di Agency B possa accettare un invite di Agency A.
        if ($request->user()) {
            $contactAgencyId = $contact->agencyClient?->agency_id;
            $userAgencyId    = $request->user()->agencyMembers()
                ->where('status', 'active')
                ->value('agency_id');

            if ($contactAgencyId && $userAgencyId && $contactAgencyId !== $userAgencyId) {
                abort(403, 'Non hai i permessi per accettare questo invito.');
            }
        }

        $request->validate([
            'password' => ['required', 'string', 'min:8', 'confirmed'],
        ]);

        $tenant = $contact->inviteTenant;

        $this->inviteService->acceptInvite($contact, $request->input('password'));

        $storeUrl = $this->resolveStoreUrl($tenant);

        return redirect()->route('client-invite.accepted')->with([
            'storeName' => $tenant?->name,
            'storeUrl'  => $storeUrl,
            'email'     => $contact->email,
        ]);
    }

    /**
     * Success page shown after a successful invite acceptance.
     */
    public function accepted(): View
    {
        return view('client-invite.accepted', [
            'storeName' => session('storeName', ''),
            'storeUrl'  => session('storeUrl', ''),
            'email'     => session('email', ''),
        ]);
    }

    /**
     * Generic invalid/expired invite page.
     */
    public function invalid(): View
    {
        return view('client-invite.invalid', [
            'reason' => session('reason', 'invalid'),
        ]);
    }

    // ── Helpers ───────────────────────────────────────────────────────────────

    private function resolveStoreUrl(?object $tenant): string
    {
        if (! $tenant) {
            return '#';
        }

        $domain = $tenant->domains()->first()?->domain;

        if (! $domain) {
            return '#';
        }

        $scheme = app()->isProduction() ? 'https' : 'http';

        return "{$scheme}://{$domain}/admin";
    }
}
