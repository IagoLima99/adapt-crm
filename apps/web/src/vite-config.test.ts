import { describe, expect, it } from "vitest";

import { createApiProxy } from "../vite.config";

describe("Vite development API proxy", () => {
  it("uses the configured API origin and removes the public /api prefix", () => {
    const proxy = createApiProxy("http://127.0.0.1:9000");

    expect(proxy.target).toBe("http://127.0.0.1:9000");
    expect(proxy.changeOrigin).toBe(true);
    expect(proxy.rewrite("/api/health")).toBe("/health");
  });
});
