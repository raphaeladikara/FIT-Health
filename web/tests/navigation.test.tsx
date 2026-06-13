import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { SideNavigation } from "@/components/shell/side-navigation";

vi.mock("next/navigation", () => ({
  usePathname: () => "/resources",
}));

describe("side navigation", () => {
  it("marks the current workspace and exposes the operational labels", () => {
    render(<SideNavigation />);

    expect(screen.getByRole("navigation", { name: "Primary navigation" })).toBeVisible();
    for (const label of [
      "Command Center",
      "Patient Review",
      "Batch Intake",
      "Resource Scenarios",
      "Trust Center",
    ]) {
      expect(screen.getByRole("link", { name: new RegExp(label, "i") })).toBeVisible();
    }
    expect(screen.getByRole("link", { name: /Resource Scenarios/i })).toHaveAttribute(
      "aria-current",
      "page",
    );
    expect(screen.getByRole("link", { name: /Patient Review/i })).not.toHaveAttribute(
      "aria-current",
    );
  });
});
