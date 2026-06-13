import { describe, expect, it } from "vitest";

import { paginate } from "@/lib/pagination";

const items = Array.from({ length: 57 }, (_, i) => i + 1);

describe("paginate", () => {
  it("uses the given page size", () => {
    const page = paginate(items, 1, 25);
    expect(page.items).toHaveLength(25);
    expect(page.items[0]).toBe(1);
    expect(page.totalPages).toBe(3);
    expect(page.total).toBe(57);
  });

  it("returns the remainder on the last page", () => {
    const page = paginate(items, 3, 25);
    expect(page.items).toHaveLength(7);
    expect(page.items[0]).toBe(51);
  });

  it("clamps an out-of-range page into bounds", () => {
    expect(paginate(items, 99, 25).currentPage).toBe(3);
    expect(paginate(items, 0, 25).currentPage).toBe(1);
    expect(paginate(items, -4, 25).currentPage).toBe(1);
  });

  it("reports one page for an empty list", () => {
    const page = paginate([], 1, 25);
    expect(page.totalPages).toBe(1);
    expect(page.items).toHaveLength(0);
  });
});
