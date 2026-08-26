import { describe, expect, it, vi } from "vitest";

import { ApiClient, ApiError, type ProblemDetails } from "./client";

function parseStatus(value: unknown): { status: string } {
  if (
    typeof value !== "object" ||
    value === null ||
    !("status" in value) ||
    typeof value.status !== "string"
  ) {
    throw new TypeError("Expected a status response.");
  }

  return { status: value.status };
}

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

    const result = await client.get("/health", parseStatus);

    expect(result).toEqual({ status: "ok" });
    expect(fetchImplementation).toHaveBeenCalledOnce();
    expect(fetchImplementation.mock.calls[0]?.[0]).toEqual(
      new URL("https://api.example.test/v1/health"),
    );
  });

  it("requires successful responses to satisfy the provided parser", async () => {
    const fetchImplementation = vi
      .fn<typeof fetch>()
      .mockResolvedValue(new Response(JSON.stringify({ status: 200 })));
    const client = new ApiClient(
      "https://api.example.test",
      fetchImplementation,
    );

    await expect(client.get("/health", parseStatus)).rejects.toThrow(
      "Expected a status response.",
    );
  });

  it("preserves Problem Details for unsuccessful responses", async () => {
    const problem: ProblemDetails = {
      type: "https://api.example.test/problems/unavailable",
      title: "Service unavailable",
      status: 503,
      detail: "Try again later.",
      instance: "/api/v1/health",
      code: "service_unavailable",
      correlation_id: "correlation-123",
    };
    const fetchImplementation = vi.fn<typeof fetch>().mockResolvedValue(
      new Response(JSON.stringify(problem), {
        headers: { "Content-Type": "application/problem+json" },
        status: 503,
      }),
    );
    const client = new ApiClient(
      "https://api.example.test",
      fetchImplementation,
    );

    await expect(client.get("/health", parseStatus)).rejects.toEqual(
      new ApiError(problem),
    );
  });

  it("uses a safe typed fallback for invalid error responses", async () => {
    const fetchImplementation = vi
      .fn<typeof fetch>()
      .mockResolvedValue(new Response(null, { status: 503 }));
    const client = new ApiClient(
      "https://api.example.test",
      fetchImplementation,
    );

    await expect(client.get("/health", parseStatus)).rejects.toMatchObject({
      problem: {
        status: 503,
        code: "unexpected_http_error",
        instance: "https://api.example.test/health",
      },
    });
  });

  it("rejects absolute URLs before forwarding request headers", async () => {
    const fetchImplementation = vi.fn<typeof fetch>();
    const client = new ApiClient(
      "https://api.example.test",
      fetchImplementation,
    );

    await expect(
      client.get("https://attacker.example/collect", parseStatus, {
        headers: { Authorization: "Bearer secret" },
      }),
    ).rejects.toThrow("API request paths must be relative.");
    expect(fetchImplementation).not.toHaveBeenCalled();
  });
});
