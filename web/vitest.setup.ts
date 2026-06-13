import "@testing-library/jest-dom/vitest";

import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// `globals` is off, so Testing Library's automatic cleanup never registers.
// Unmount between tests so renders don't leak across cases in the same file.
afterEach(() => {
  cleanup();
});
