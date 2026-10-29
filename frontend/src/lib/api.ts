/**
 * Typed client for the User Story Generator API.
 */

const API_BASE = (
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000"
).replace(/\/+$/, "");

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status?: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export interface AudioGenerationResult {
  story: string;
  transcription: string;
}

async function extractError(response: Response): Promise<string> {
  try {
    const body = await response.json();
    if (typeof body?.detail === "string") return body.detail;
  } catch {
    // fall through to the generic message
  }
  return `Request failed with status ${response.status}`;
}

async function postForm<T>(path: string, formData: FormData): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, { method: "POST", body: formData });
  } catch {
    throw new ApiError(
      `Cannot reach the API at ${API_BASE}. Is the backend running?`,
    );
  }

  if (!response.ok) {
    throw new ApiError(await extractError(response), response.status);
  }
  return (await response.json()) as T;
}

/** Generate a user story from a typed feature description. */
export async function generateFromText(
  text: string,
  token: string,
): Promise<string> {
  const formData = new FormData();
  formData.append("text", text);
  formData.append("token", token);

  const { story } = await postForm<{ story: string }>(
    "/generate_from_text",
    formData,
  );
  return story;
}

/** Transcribe an audio note and generate a user story from it. */
export async function generateFromAudio(
  file: File,
  token: string,
): Promise<AudioGenerationResult> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("token", token);

  return postForm<AudioGenerationResult>("/generate_from_audio", formData);
}
