import { describe, expect, it, vi } from "vitest";

import { ApiClient, ApiError } from "./client";

describe("ApiClient", () => {
  it("resolves paths against the configured API base URL", async () => {
    const fetchImplementation = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(JSON.stringify({ status: "ok" }), {
        headers: { "Content-Type": "application/json" },
        status: 200,
      }),
    );
    const client = new ApiClient(
      "https://api.example.test/v1",
      fetchImplementation,
    );

    const result = await client.get<{ status: string }>("/health");

    expect(result).toEqual({ status: "ok" });
    expect(fetchImplementation).toHaveBeenCalledOnce();
    expect(fetchImplementation.mock.calls[0]?.[0]).toEqual(
      new URL("https://api.example.test/v1/health"),
    );
  });

  it("raises a typed error for unsuccessful responses", async () => {
    const fetchImplementation = vi
      .fn<typeof fetch>()
      .mockResolvedValue(new Response(null, { status: 503 }));
    const client = new ApiClient(
      "https://api.example.test",
      fetchImplementation,
    );

    await expect(client.get("/health")).rejects.toEqual(
      new ApiError(503, ""),
    );
  });
});
