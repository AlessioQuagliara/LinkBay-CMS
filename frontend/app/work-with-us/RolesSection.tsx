"use client";

import { useState } from "react";

export type JobPosition = {
  id: number;
  title: string;
  slug: string;
  department: string;
  location: string;
  work_mode: "remote" | "hybrid" | "on_site";
  employment_type: "full_time" | "part_time" | "contract" | "internship";
  summary: string;
  featured: boolean;
};

const WORK_MODE_LABEL: Record<string, string> = {
  remote: "Remote",
  hybrid: "Hybrid",
  on_site: "On-site",
};

const EMPLOYMENT_LABEL: Record<string, string> = {
  full_time: "Full-time",
  part_time: "Part-time",
  contract: "Contract",
  internship: "Internship",
};

interface Props {
  positions: JobPosition[];
  applyBaseUrl: string;
}

export default function RolesSection({ positions, applyBaseUrl }: Props) {
  const departments = ["All", ...Array.from(new Set(positions.map((p) => p.department))).sort()];
  const [selectedDept, setSelectedDept] = useState("All");

  const filtered = positions.filter(
    (p) => selectedDept === "All" || p.department === selectedDept
  );

  if (positions.length === 0) {
    return (
      <div className="text-center py-16 text-gray-500">
        <p className="text-lg mb-2">No open roles right now.</p>
        <p className="text-sm">
          If you think you are a fit,{" "}
          <a href="mailto:info@linkbay-cms.com" className="text-[#ff5758] hover:underline">
            introduce yourself
          </a>
          .
        </p>
      </div>
    );
  }

  return (
    <>
      {/* Department filter */}
      <div className="flex flex-wrap gap-2 justify-center mb-8">
        {departments.map((dept) => (
          <button
            key={dept}
            onClick={() => setSelectedDept(dept)}
            className={`px-4 py-2 rounded-full text-sm font-semibold transition-colors ${
              selectedDept === dept
                ? "bg-[#ff5758] text-white"
                : "bg-white text-gray-600 border border-gray-200 hover:border-[#ff5758]"
            }`}
          >
            {dept}
          </button>
        ))}
      </div>

      {/* Roles list */}
      <div className="space-y-4">
        {filtered.map((role) => (
          <div
            key={role.id}
            className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 flex flex-col sm:flex-row sm:items-center gap-4"
          >
            <div className="flex-1 min-w-0">
              <div className="flex flex-wrap gap-2 mb-2">
                {role.featured && (
                  <span className="bg-[#ff5758] text-white px-2.5 py-0.5 rounded text-xs font-semibold">
                    Featured
                  </span>
                )}
                <span className="bg-blue-50 text-blue-700 px-2.5 py-0.5 rounded text-xs font-medium">
                  {EMPLOYMENT_LABEL[role.employment_type] ?? role.employment_type}
                </span>
                <span className="bg-green-50 text-green-700 px-2.5 py-0.5 rounded text-xs font-medium">
                  {role.location}
                </span>
                <span className="bg-gray-100 text-gray-600 px-2.5 py-0.5 rounded text-xs font-medium">
                  {WORK_MODE_LABEL[role.work_mode] ?? role.work_mode}
                </span>
                <span className="bg-purple-50 text-purple-700 px-2.5 py-0.5 rounded text-xs font-medium">
                  {role.department}
                </span>
              </div>

              <h3 className="text-lg font-bold text-[#343a4D] mb-1">{role.title}</h3>
              <p className="text-gray-600 text-sm leading-relaxed line-clamp-2">{role.summary}</p>
            </div>

            <div className="shrink-0">
              <a
                href={`${applyBaseUrl}/careers/apply/${role.slug}`}
                className="inline-block px-5 py-2.5 bg-[#ff5758] text-white text-sm font-semibold rounded-lg hover:bg-[#e04e4f] transition-colors whitespace-nowrap"
              >
                Apply now
              </a>
            </div>
          </div>
        ))}

        {filtered.length === 0 && selectedDept !== "All" && (
          <div className="text-center py-8 text-gray-500">
            No open roles in {selectedDept} right now.
          </div>
        )}
      </div>
    </>
  );
}
