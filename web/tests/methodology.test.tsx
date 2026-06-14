import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import MethodologyPage from "@/app/(public)/methodology/page";
import { TermHelp } from "@/components/ui/term-help";
import { GLOSSARY } from "@/lib/glossary";

describe("methodology page", () => {
  it("documents the major methods and a linkable glossary", () => {
    render(<MethodologyPage />);

    for (const heading of [
      "Feature stages",
      "Validation strategy",
      "Per-label thresholds",
      "Artifact provenance",
      "Limitations & ethics",
      "Glossary",
    ]) {
      expect(screen.getByRole("heading", { name: heading })).toBeVisible();
    }

    // Every glossary term has a directly linkable anchor.
    for (const slug of Object.keys(GLOSSARY)) {
      expect(document.getElementById(`glossary-${slug}`)).toBeTruthy();
    }
  });
});

describe("TermHelp", () => {
  it("links a term to its glossary anchor", () => {
    render(<TermHelp slug="leakage" />);
    expect(
      screen.getByRole("link", { name: /Diagnostic leakage — see definition/i }),
    ).toHaveAttribute("href", "/methodology#glossary-leakage");
  });
});
