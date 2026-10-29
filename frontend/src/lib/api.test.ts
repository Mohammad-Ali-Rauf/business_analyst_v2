import { afterEach, describe, expect, it, vi } from "vitest";

import { ApiError, generateFromAudio, generateFromText } from "./api";

async function jsonResponse(
  body: unknown,
  init: { ok?: boolean; status?: number } = {},
): Promise<Response> {
  return {
    ok: init.ok ?? true,
    status: init.status ?? 200,
    json: async () => body,
  } as unknown as Response;
}

afterEach(() => {
  vi.unstubAllGlobals();
});

describe("generateFromText", () => {
  it("posts the feature and session token to the text endpoint", async () => {
    const fetchSpy = vi.fn<(url: string, init?: RequestInit) => Promise<Response>>(
      () => jsonResponse({ story: "## User Story" }),
    );
    vi.stubGlobal("fetch", fetchSpy);

    const story = await generateFromText("a feature", "session-1");

    expect(story).toBe("## User Story");
    const [url, init] = fetchSpy.mock.calls[0];
    expect(url).toBe("http://localhost:8000/generate_from_text");
    expect(init?.method).toBe("POST");
    const body = init?.body as FormData;
    expect(body.get("text")).toBe("a feature");
    expect(body.get("token")).toBe("session-1");
  });

  it("surfaces the server's error detail with its status", async () => {
    vi.stubGlobal("fetch", () =>
      jsonResponse({ detail: "'text' must not be empty" }, { ok: false, status: 422 }),
    );

    const request = generateFromText("", "session-1");

    await expect(request).rejects.toMatchObject({
      name: "ApiError",
      message: "'text' must not be empty",
      status: 422,
    });
  });

  it("falls back to a generic message when the body has no detail", async () => {
    vi.stubGlobal("fetch", () => jsonResponse({}, { ok: false, status: 500 }));

    await expect(generateFromText("x", "t")).rejects.toThrow(
      "Request failed with status 500",
    );
  });

  it("handles non-JSON error bodies", async () => {
    vi.stubGlobal("fetch", () =>
      Promise.resolve({
        ok: false,
        status: 502,
        json: async () => {
          throw new Error("not json");
        },
      } as unknown as Response),
    );

    await expect(generateFromText("x", "t")).rejects.toThrow(
      "Request failed with status 502",
    );
  });

  it("reports a helpful error when the API is unreachable", async () => {
    vi.stubGlobal("fetch", () => Promise.reject(new Error("connection refused")));

    const request = generateFromText("x", "t");

    await expect(request).rejects.toThrow(
      "Cannot reach the API at http://localhost:8000. Is the backend running?",
    );
  });
});

describe("generateFromAudio", () => {
  it("posts the audio file and returns transcription and story", async () => {
    const fetchSpy = vi.fn<(url: string, init?: RequestInit) => Promise<Response>>(
      () => jsonResponse({ story: "## User Story", transcription: "a note" }),
    );
    vi.stubGlobal("fetch", fetchSpy);

    const file = new File(["audio-bytes"], "note.wav", { type: "audio/wav" });
    const result = await generateFromAudio(file, "session-1");

    expect(result).toEqual({ story: "## User Story", transcription: "a note" });
    const [url, init] = fetchSpy.mock.calls[0];
    expect(url).toBe("http://localhost:8000/generate_from_audio");
    const body = init?.body as FormData;
    expect(body.get("file")).toBeInstanceOf(Blob);
    expect(body.get("token")).toBe("session-1");
  });

  it("propagates API errors", async () => {
    vi.stubGlobal("fetch", () =>
      jsonResponse({ detail: "Audio file exceeds the 25 MB limit" }, { ok: false, status: 413 }),
    );

    const file = new File(["x"], "note.wav", { type: "audio/wav" });
    await expect(generateFromAudio(file, "t")).rejects.toBeInstanceOf(ApiError);
  });
});
