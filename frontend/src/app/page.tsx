"use client";

import { useEffect, useState } from "react";

import InputPanel from "@/components/InputPanel";
import OutputPanel from "@/components/OutputPanel";
import { ApiError, generateFromAudio, generateFromText } from "@/lib/api";

const TOKEN_STORAGE_KEY = "user_token";

export default function Home() {
  const [feature, setFeature] = useState("");
  const [story, setStory] = useState("");
  const [transcript, setTranscript] = useState<string | null>(null);
  const [audioFile, setAudioFile] = useState<File | null>(null);
  const [token, setToken] = useState("");
  const [busy, setBusy] = useState<"text" | "audio" | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Stable per-browser session token used to scope conversation memory.
  useEffect(() => {
    let userToken = localStorage.getItem(TOKEN_STORAGE_KEY);
    if (!userToken) {
      userToken = crypto.randomUUID();
      localStorage.setItem(TOKEN_STORAGE_KEY, userToken);
    }
    setToken(userToken);
  }, []);

  async function handleGenerateFromText() {
    if (!feature.trim() || busy) return;
    setBusy("text");
    setError(null);
    setTranscript(null);
    try {
      setStory(await generateFromText(feature, token));
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Unexpected error occurred");
    } finally {
      setBusy(null);
    }
  }

  async function handleGenerateFromAudio() {
    if (!audioFile || busy) return;
    setBusy("audio");
    setError(null);
    try {
      const result = await generateFromAudio(audioFile, token);
      setTranscript(result.transcription);
      setFeature(result.transcription);
      setStory(result.story);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Unexpected error occurred");
    } finally {
      setBusy(null);
    }
  }

  function handleClear() {
    setStory("");
    setTranscript(null);
    setError(null);
    setFeature("");
    setAudioFile(null);
  }

  return (
    <div className="mx-auto flex min-h-screen max-w-6xl flex-col px-6 py-8">
      <header className="mb-8 flex flex-col gap-2">
        <div className="flex items-center gap-3">
          <span className="flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br from-accent to-violet shadow-lg shadow-accent/30">
            <svg
              className="h-6 w-6 text-white"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={2}
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
              />
            </svg>
          </span>
          <div>
            <h1 className="text-2xl font-bold tracking-tight text-fg sm:text-3xl">
              Agile User Story Generator
            </h1>
            <p className="text-sm text-muted">
              From raw feature ideas to backlog-ready user stories in seconds.
            </p>
          </div>
        </div>
      </header>

      <main className="grid flex-1 grid-cols-1 gap-6 lg:grid-cols-2">
        <InputPanel
          feature={feature}
          onFeatureChange={setFeature}
          audioFile={audioFile}
          onAudioFileChange={setAudioFile}
          onGenerateFromText={handleGenerateFromText}
          onGenerateFromAudio={handleGenerateFromAudio}
          busy={busy}
        />
        <OutputPanel
          story={story}
          transcript={transcript}
          busy={busy}
          error={error}
          onClear={handleClear}
        />
      </main>

      <footer className="mt-10 border-t border-line pt-5 text-center text-xs text-muted/70">
        Powered by FastAPI · Google Gemini · OpenAI Whisper · Qdrant —
        stories are generated from your session context and may need review.
      </footer>
    </div>
  );
}
