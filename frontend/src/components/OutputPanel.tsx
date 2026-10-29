"use client";

import { useState } from "react";
import Markdown from "react-markdown";

interface OutputPanelProps {
  story: string;
  transcript: string | null;
  busy: "text" | "audio" | null;
  error: string | null;
  onClear: () => void;
}

export default function OutputPanel({
  story,
  transcript,
  busy,
  error,
  onClear,
}: OutputPanelProps) {
  const [copied, setCopied] = useState(false);

  async function copyStory() {
    if (!story) return;
    try {
      await navigator.clipboard.writeText(story);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Clipboard unavailable (e.g. insecure context) — silently ignore.
    }
  }

  function downloadStory() {
    if (!story) return;
    const blob = new Blob([story], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = `user-story-${new Date().toISOString().slice(0, 10)}.md`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  return (
    <section className="animate-rise flex flex-col rounded-2xl border border-line bg-panel/70 p-6 shadow-xl shadow-black/20">
      <header className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h2 className="text-lg font-semibold text-fg">Generated story</h2>
          <p className="mt-1 text-sm text-muted">
            Structured markdown — ready to drop into your backlog.
          </p>
        </div>
        {story && (
          <div className="flex shrink-0 items-center gap-2">
            <button
              type="button"
              onClick={copyStory}
              className="rounded-lg border border-line bg-panel-soft px-3 py-1.5 text-xs font-medium text-muted transition hover:border-accent hover:text-accent-soft"
            >
              {copied ? "Copied ✓" : "Copy"}
            </button>
            <button
              type="button"
              onClick={downloadStory}
              className="rounded-lg border border-line bg-panel-soft px-3 py-1.5 text-xs font-medium text-muted transition hover:border-accent hover:text-accent-soft"
            >
              Download .md
            </button>
            <button
              type="button"
              onClick={onClear}
              className="rounded-lg border border-line bg-panel-soft px-3 py-1.5 text-xs font-medium text-muted transition hover:border-rose hover:text-rose"
            >
              Clear
            </button>
          </div>
        )}
      </header>

      {error && (
        <div className="mb-4 rounded-xl border border-rose/40 bg-rose/10 px-4 py-3 text-sm text-rose">
          <span className="font-semibold">Something went wrong: </span>
          {error}
        </div>
      )}

      {transcript && (
        <div className="mb-4 rounded-xl border border-line bg-ink/50 px-4 py-3">
          <p className="text-[11px] font-semibold uppercase tracking-wider text-accent-soft">
            Transcript
          </p>
          <p className="mt-1 text-sm text-muted">{transcript}</p>
        </div>
      )}

      <div className="min-h-[320px] flex-1 rounded-xl border border-line/60 bg-ink/40 p-5">
        {busy ? (
          <div className="animate-pulse-soft space-y-3" aria-hidden="true">
            <div className="h-5 w-2/5 rounded bg-panel-soft" />
            <div className="h-3 w-4/5 rounded bg-panel-soft" />
            <div className="h-3 w-3/5 rounded bg-panel-soft" />
            <div className="h-5 w-1/4 rounded bg-panel-soft pt-2" />
            <div className="h-3 w-full rounded bg-panel-soft" />
            <div className="h-3 w-11/12 rounded bg-panel-soft" />
            <div className="h-3 w-3/4 rounded bg-panel-soft" />
            <div className="h-5 w-1/3 rounded bg-panel-soft pt-2" />
            <div className="h-3 w-5/6 rounded bg-panel-soft" />
            <div className="h-3 w-2/3 rounded bg-panel-soft" />
          </div>
        ) : story ? (
          <article className="markdown-body">
            <Markdown>{story}</Markdown>
          </article>
        ) : (
          <div className="flex h-full min-h-[280px] flex-col items-center justify-center text-center">
            <svg
              className="mb-4 h-12 w-12 text-line"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
              strokeWidth={1.5}
              aria-hidden="true"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                d="M19.5 14.25v-2.625a3.375 3.375 0 00-3.375-3.375h-1.5A1.125 1.125 0 0113.5 7.125v-1.5a3.375 3.375 0 00-3.375-3.375H8.25m2.25 0H5.625c-.621 0-1.125.504-1.125 1.125v17.25c0 .621.504 1.125 1.125 1.125h12.75c.621 0 1.125-.504 1.125-1.125V11.25a9 9 0 00-9-9z"
              />
            </svg>
            <p className="text-sm font-medium text-muted">
              No story generated yet
            </p>
            <p className="mt-1 max-w-xs text-xs text-muted/70">
              Describe a feature on the left and hit generate — the user story,
              acceptance criteria and test scenarios will appear here.
            </p>
          </div>
        )}
      </div>
    </section>
  );
}
