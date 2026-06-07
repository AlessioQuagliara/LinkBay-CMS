<?php

declare(strict_types=1);

namespace App\Http\Controllers;

use App\Services\AgencyMemberService;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;

class AgencyMemberInviteController extends Controller
{
    public function __construct(private readonly AgencyMemberService $service) {}

    public function show(string $token): View|RedirectResponse
    {
        $member = $this->service->findByToken($token);

        if (! $member) {
            return redirect()->route('agency-invite.invalid');
        }

        if ($member->isInviteExpired()) {
            return redirect()->route('agency-invite.invalid')->with('reason', 'expired');
        }

        $agencyName = null;
        try {
            $agencyName = $member->agency?->brand_name;
        } catch (\Throwable) {
        }

        return view('agency-invite.show', [
            'member' => $member,
            'agencyName' => $agencyName ?? '—',
            'token' => $token,
        ]);
    }

    public function accept(Request $request, string $token): RedirectResponse
    {
        $member = $this->service->findByToken($token);

        if (! $member || $member->isInviteExpired()) {
            return redirect()->route('agency-invite.invalid')->with('reason', 'expired');
        }

        $request->validate([
            'name' => ['required', 'string', 'max:150'],
            'password' => ['required', 'string', 'min:8', 'confirmed'],
        ]);

        $agencyName = null;
        $agencySlug = null;
        $agencyDomain = null;
        try {
            $agency = $member->agency;
            $agencyName = $agency?->brand_name;
            $agencySlug = $agency?->slug;
            $agencyDomain = $agency?->panelDomain();
        } catch (\Throwable) {
        }

        $this->service->acceptInvite($member, $request->input('name'), $request->input('password'));

        $scheme = app()->isProduction() ? 'https' : 'http';
        $panelUrl = $agencyDomain ? "{$scheme}://{$agencyDomain}/dashboard" : '#';

        return redirect()->route('agency-invite.accepted')->with([
            'agencyName' => $agencyName,
            'panelUrl' => $panelUrl,
            'email' => $member->invited_email,
        ]);
    }

    public function accepted(): View
    {
        return view('agency-invite.accepted', [
            'agencyName' => session('agencyName', ''),
            'panelUrl' => session('panelUrl', ''),
            'email' => session('email', ''),
        ]);
    }

    public function invalid(): View
    {
        return view('agency-invite.invalid', [
            'reason' => session('reason', 'invalid'),
        ]);
    }
}
