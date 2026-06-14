"use client";

import { Search, Stethoscope } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { ArtifactStatus } from "@/components/ui/artifact-status";
import type { Manifest } from "@/lib/types";

function normaliseCase(raw: string): string {
  const value = raw.trim();
  if (/^\d+$/.test(value)) return `Case ${value.padStart(3, "0")}`;
  return value;
}

export function TopBar({ manifest }: { manifest: Manifest }) {
  const router = useRouter();
  const [query, setQuery] = useState("");

  function onSubmit(event: FormEvent) {
    event.preventDefault();
    const value = query.trim();
    if (!value) return;
    router.push(`/patients?case=${encodeURIComponent(normaliseCase(value))}`);
  }

  return (
    <div className="top-bar">
      <form className="top-search" role="search" onSubmit={onSubmit}>
        <Search aria-hidden="true" size={18} />
        <input
          type="search"
          value={query}
          onChange={(event) => setQuery(event.target.value)}
          placeholder="Find a case (e.g. 042 or Case 042)"
          aria-label="Find an anonymous case by ID"
        />
      </form>
      <div className="top-bar-spacer" />
      <div className="top-actions">
        <ArtifactStatus manifest={manifest} />
        <div className="profile-chip">
          <span className="avatar" aria-hidden="true">
            <Stethoscope size={17} />
          </span>
          <span>
            <strong>PRE_LAB model</strong>
            <small>{manifest.execution_profile} · decision support</small>
          </span>
        </div>
      </div>
    </div>
  );
}
