export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly statusText: string,
  ) {
    super(`API request failed with status ${status}.`);
    this.name = "ApiError";
  }
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

  async get<T>(path: string, init: Omit<RequestInit, "method"> = {}): Promise<T> {
    const headers = new Headers(init.headers);
    if (!headers.has("Accept")) {
      headers.set("Accept", "application/json");
    }

    const response = await this.fetchImplementation(
      new URL(path.replace(/^\/+/, ""), this.baseUrl),
      {
        ...init,
        headers,
        method: "GET",
      },
    );

    if (!response.ok) {
      throw new ApiError(response.status, response.statusText);
    }

    return (await response.json()) as T;
  }
}
