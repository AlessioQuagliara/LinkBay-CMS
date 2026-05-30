<?php

namespace App\Http\Controllers;

use App\Models\Central\JobApplication;
use App\Models\Central\JobPosition;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Storage;

class CareersController extends Controller
{
    public function apply(JobPosition $job)
    {
        if ($job->status !== 'published') {
            abort(404);
        }

        return view('careers.apply', compact('job'));
    }

    public function submit(Request $request, JobPosition $job)
    {
        if ($job->status !== 'published') {
            abort(404);
        }

        $validated = $request->validate([
            'full_name'          => ['required', 'string', 'max:150'],
            'email'              => ['required', 'email', 'max:255'],
            'phone'              => ['nullable', 'string', 'max:50'],
            'location'           => ['nullable', 'string', 'max:150'],
            'linkedin_url'       => ['nullable', 'url', 'max:500'],
            'portfolio_url'      => ['nullable', 'url', 'max:500'],
            'motivation'         => ['required', 'string', 'max:5000'],
            'experience_summary' => ['required', 'string', 'max:5000'],
            'cv'                 => ['required', 'file', 'mimes:pdf,doc,docx', 'max:10240'],
        ]);

        $cv = $request->file('cv');
        $filename = \Illuminate\Support\Str::uuid() . '.' . $cv->getClientOriginalExtension();
        $cvPath = $cv->storeAs('careers/cvs', $filename, 'local');

        JobApplication::create([
            'job_position_id'    => $job->id,
            'full_name'          => $validated['full_name'],
            'email'              => $validated['email'],
            'phone'              => $validated['phone'] ?? null,
            'location'           => $validated['location'] ?? null,
            'linkedin_url'       => $validated['linkedin_url'] ?? null,
            'portfolio_url'      => $validated['portfolio_url'] ?? null,
            'motivation'         => $validated['motivation'],
            'experience_summary' => $validated['experience_summary'],
            'cv_path'            => $cvPath,
            'ip_address'         => $request->ip(),
        ]);

        return redirect()->route('careers.success', $job->slug);
    }

    public function success(string $slug)
    {
        $job = JobPosition::where('slug', $slug)->firstOrFail();
        return view('careers.success', compact('job'));
    }

    public function downloadCv(JobApplication $application)
    {
        abort_unless(Storage::disk('local')->exists($application->cv_path), 404);

        $ext = pathinfo($application->cv_path, PATHINFO_EXTENSION);
        $filename = \Illuminate\Support\Str::slug($application->full_name) . '-cv.' . $ext;

        return Storage::disk('local')->download($application->cv_path, $filename);
    }
}
