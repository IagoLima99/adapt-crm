import { describe, expect, it } from "vitest";

import { createBuildMetadata } from "./build-metadata.mjs";

describe("createBuildMetadata", () => {
  it("records the release version and immutable commit", () => {
    expect(createBuildMetadata("0.1.0", "abc123")).toEqual({
      version: "0.1.0",
      commit: "abc123",
    });
  });

  it.each(["version", "commit"])("rejects an empty %s", (field) => {
    const version = field === "version" ? "" : "0.1.0";
    const commit = field === "commit" ? "" : "abc123";

    expect(() => createBuildMetadata(version, commit)).toThrow(
      "Build version and commit are required.",
    );
  });
});
