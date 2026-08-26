export interface ProblemDetails {
  type: string;
  title: string;
  status: number;
  detail: string;
  instance: string;
  code: string;
  correlation_id: string;
  errors?: unknown;
}

export type JsonParser<T> = (value: unknown) => T;

export class ApiError extends Error {
  constructor(readonly problem: ProblemDetails) {
    super(problem.title);
    this.name = "ApiError";
  }

  get status(): number {
    return this.problem.status;
  }
}

function isProblemDetails(value: unknown): value is ProblemDetails {
  if (typeof value !== "object" || value === null) {
    return false;
  }

  const problem = value as Record<string, unknown>;
  return (
    typeof problem.type === "string" &&
    typeof problem.title === "string" &&
    typeof problem.status === "number" &&
    typeof problem.detail === "string" &&
    typeof problem.instance === "string" &&
    typeof problem.code === "string" &&
    typeof problem.correlation_id === "string"
  );
}

async function readProblemDetails(
  response: Response,
  requestUrl: URL,
): Promise<ProblemDetails> {
  const contentType = response.headers.get("Content-Type")?.split(";", 1)[0];

  if (contentType?.trim().toLowerCase() === "application/problem+json") {
    try {
      const body: unknown = await response.json();
      if (isProblemDetails(body)) {
        return body;
      }
    } catch {
      // A non-compliant response is represented by the safe fallback below.
    }
  }

  return {
    type: "about:blank",
    title: response.statusText || "API request failed",
    status: response.status,
    detail: "The API returned an invalid or empty error response.",
    instance: requestUrl.toString(),
    code: "unexpected_http_error",
    correlation_id: response.headers.get("X-Correlation-ID") ?? "",
  };
}

function resolveRequestUrl(path: string, baseUrl: URL): URL {
  if (/^[a-z][a-z\d+.-]*:/i.test(path) || /^[\\/]{2}/.test(path)) {
    throw new TypeError("API request paths must be relative.");
  }

  const requestUrl = new URL(path.replace(/^\/+/, ""), baseUrl);
  if (requestUrl.origin !== baseUrl.origin) {
    throw new TypeError("API request paths must use the configured origin.");
  }

  return requestUrl;
}

export class ApiClient {
  private readonly baseUrl: URL;

  constructor(
    baseUrl: string,
    private readonly fetchImplementation: typeof fetch = fetch,
  ) {
    this.baseUrl = new URL(baseUrl);
    if (!this.baseUrl.pathname.endsWith("/")) {
      this.baseUrl.pathname += "/";
    }
  }

  async get<T>(
    path: string,
    parse: JsonParser<T>,
    init: Omit<RequestInit, "method"> = {},
  ): Promise<T> {
    const requestUrl = resolveRequestUrl(path, this.baseUrl);
    const headers = new Headers(init.headers);
    if (!headers.has("Accept")) {
      headers.set("Accept", "application/json");
    }

    const response = await this.fetchImplementation(requestUrl, {
      ...init,
      headers,
      method: "GET",
    });

    if (!response.ok) {
      throw new ApiError(await readProblemDetails(response, requestUrl));
    }

    const body: unknown = await response.json();
    return parse(body);
  }
}
