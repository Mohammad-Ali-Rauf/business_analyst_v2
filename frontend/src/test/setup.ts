import "@testing-library/jest-dom/vitest";

import { cleanup } from "@testing-library/react";
import { afterEach } from "vitest";

// Without vitest globals, React Testing Library cannot register its own
// auto-cleanup, so unmount the rendered trees explicitly after each test.
afterEach(() => {
  cleanup();
});
