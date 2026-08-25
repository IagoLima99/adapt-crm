import { renderToStaticMarkup } from "react-dom/server";
import { MemoryRouter } from "react-router";
import { describe, expect, it } from "vitest";

import { App } from "./App";

function renderPath(path: string) {
  return renderToStaticMarkup(
    <MemoryRouter initialEntries={[path]}>
      <App />
    </MemoryRouter>,
  );
}

describe("App routing", () => {
  it("renders the technical bootstrap route", () => {
    expect(renderPath("/")).toContain("Fundação pronta");
  });

  it("renders the fallback route", () => {
    expect(renderPath("/unknown")).toContain("Página não encontrada");
  });
});
