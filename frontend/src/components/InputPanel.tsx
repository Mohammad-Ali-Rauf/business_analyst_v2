"use client";

import { useRef, useState } from "react";

const SAMPLE_PROMPTS = [
  "As a shopper, I want to save items to a wishlist so that I can buy them later.",
  "Users should be able to reset their password via a secure email link.",
  "Add multi-factor authentication for admin accounts.",
  "Let customers track their orders in real time from the mobile app.",
];

interface InputPanelProps {
  feature: string;
  onFeatureChange: (value: string) => void;
  audioFile: File | null;
  onAudioFileChange: (file: File | null) => void;
  onGenerateFromText: () => void;
  onGenerateFromAudio: () => void;
  busy: "text" | "audio" | null;
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

export default function InputPanel({
  feature,
  onFeatureChange,
  audioFile,
  onAudioFileChange,
  onGenerateFromText,
  onGenerateFromAudio,
  busy,
}: InputPanelProps) {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [dragActive, setDragActive] = useState(false);

  const textBusy = busy === "text";
  const audioBusy = busy === "audio";
  const anyBusy = busy !== null;

  return (
    <section className="animate-rise flex flex-col rounded-2xl border border-line bg-panel/70 p-6 shadow-xl shadow-black/20">
      <header className="mb-4">
        <h2 className="text-lg font-semibold text-fg">Describe the feature</h2>
        <p className="mt-1 text-sm text-muted">
          Type a requirement or drop a voice note — the assistant drafts the
          story.
        </p>
      </header>

      <div className="relative">
        <textarea
          rows={8}
          value={feature}
          onChange={(e) => onFeatureChange(e.target.value)}
          onKeyDown={(e) => {
            if ((e.metaKey || e.ctrlKey) && e.key === "Enter") {
              e.preventDefault();
              if (!anyBusy && feature.trim()) onGenerateFromText();
            }
          }}
          placeholder="e.g. As a customer, I want to reset my password by email so that I can regain access to my account securely."
          className="w-full resize-y rounded-xl border border-line bg-ink/70 p-4 text-sm text-fg placeholder-muted/70 transition focus:border-accent focus:outline-none focus:ring-2 focus:ring-accent/40"
        />
        <span className="pointer-events-none absolute bottom-3 right-4 text-[11px] tabular-nums text-muted/70">
          {feature.length} chars
        </span>
      </div>

      <div className="mt-3 flex flex-wrap gap-2">
        {SAMPLE_PROMPTS.map((sample) => (
          <button
            key={sample}
            type="button"
            onClick={() => onFeatureChange(sample)}
            disabled={anyBusy}
            title={sample}
            className="max-w-full truncate rounded-full border border-line bg-panel-soft px-3 py-1 text-xs text-muted transition hover:border-accent hover:text-accent-soft disabled:opacity-50"
          >
            {sample}
          </button>
        ))}
      </div>

      <button
        type="button"
        onClick={onGenerateFromText}
        disabled={anyBusy || !feature.trim()}
        className="mt-5 flex items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-accent to-violet px-5 py-3 text-sm font-semibold text-white transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {textBusy ? (
          <>
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-white/40 border-t-white" />
            Generating…
          </>
        ) : (
          <>Generate user story</>
        )}
      </button>
      <p className="mt-2 text-center text-[11px] text-muted/70">
        Tip: press <kbd className="rounded border border-line px-1">Ctrl</kbd> +{" "}
        <kbd className="rounded border border-line px-1">Enter</kbd> to generate
      </p>

      <div className="my-6 flex items-center gap-3 text-xs text-muted/70">
        <span className="h-px flex-1 bg-line" />
        or use a voice note
        <span className="h-px flex-1 bg-line" />
      </div>

      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragActive(true);
        }}
        onDragLeave={() => setDragActive(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragActive(false);
          const file = e.dataTransfer.files?.[0];
          if (file) onAudioFileChange(file);
        }}
        onClick={() => fileInputRef.current?.click()}
        className={`flex cursor-pointer flex-col items-center justify-center gap-2 rounded-xl border border-dashed p-5 text-center transition ${
          dragActive
            ? "border-accent bg-accent/10"
            : "border-line bg-ink/40 hover:border-accent/60"
        }`}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="audio/*"
          className="hidden"
          onChange={(e) => onAudioFileChange(e.target.files?.[0] ?? null)}
        />
        <svg
          className="h-6 w-6 text-accent-soft"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
          strokeWidth={1.8}
          aria-hidden="true"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 18.75a6 6 0 006-6v-1.5a6 6 0 10-12 0v1.5a6 6 0 006 6zM12 18.75V21m-3.75 0h7.5M8.25 3.75h7.5"
          />
        </svg>
        {audioFile ? (
          <p className="text-sm text-fg">
            <span className="font-medium">{audioFile.name}</span>{" "}
            <span className="text-muted">({formatBytes(audioFile.size)})</span>
          </p>
        ) : (
          <p className="text-sm text-muted">
            Drag &amp; drop an audio file, or click to browse
          </p>
        )}
      </div>

      <button
        type="button"
        onClick={onGenerateFromAudio}
        disabled={anyBusy || !audioFile}
        className="mt-4 flex items-center justify-center gap-2 rounded-xl border border-accent/60 bg-accent/10 px-5 py-3 text-sm font-semibold text-accent-soft transition hover:bg-accent/20 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {audioBusy ? (
          <>
            <span className="h-4 w-4 animate-spin rounded-full border-2 border-accent-soft/40 border-t-accent-soft" />
            Transcribing &amp; generating…
          </>
        ) : (
          <>Transcribe &amp; generate</>
        )}
      </button>
    </section>
  );
}
