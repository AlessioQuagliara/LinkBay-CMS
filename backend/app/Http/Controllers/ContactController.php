<?php

namespace App\Http\Controllers;

use App\Models\Central\ContactSubmission;
use Illuminate\Http\Request;

class ContactController extends Controller
{
    public function show()
    {
        return view('contact.form');
    }

    public function store(Request $request)
    {
        $validated = $request->validate([
            'name'        => ['required', 'string', 'max:150'],
            'company'     => ['required', 'string', 'max:150'],
            'email'       => ['required', 'email', 'max:255'],
            'store_count' => ['nullable', 'string', 'max:50'],
            'message'     => ['required', 'string', 'max:5000'],
        ]);

        ContactSubmission::create([
            ...$validated,
            'ip_address' => $request->ip(),
        ]);

        return redirect()->route('contact.success');
    }

    public function success()
    {
        return view('contact.success');
    }
}
