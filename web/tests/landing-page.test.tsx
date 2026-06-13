import { render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import LandingPage from "@/app/(public)/page";

vi.mock("next/navigation", () => ({ usePathname: () => "/" }));

describe("landing page", () => {
  it("renders a single headline and the two primary paths", async () => {
    render(await LandingPage());

    expect(screen.getAllByRole("heading", { level: 1 })).toHaveLength(1);

    const demo = screen.getAllByRole("link", { name: /Start guided demo/i })[0];
    expect(demo).toHaveAttribute("href", "/demo");

    const ops = screen.getByRole("link", { name: /Open command center/i });
    expect(ops).toHaveAttribute("href", "/command-center");
  });

  it("shows five operational-flow steps and a run-status surface", async () => {
    render(await LandingPage());

    expect(document.querySelectorAll("ol.landing-flow li.flow-step")).toHaveLength(5);
    expect(screen.getByTestId("landing-run-status")).toBeVisible();
  });

  it("states four things VECTRA-X cannot claim", async () => {
    render(await LandingPage());
    const limits = document.querySelectorAll(".limit-item");
    expect(limits).toHaveLength(4);
  });
});
