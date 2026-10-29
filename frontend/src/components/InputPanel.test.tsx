import type { ComponentProps } from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import InputPanel from "./InputPanel";

type Props = ComponentProps<typeof InputPanel>;

function renderPanel(overrides: Partial<Props> = {}) {
  const props: Props = {
    feature: "",
    onFeatureChange: vi.fn(),
    audioFile: null,
    onAudioFileChange: vi.fn(),
    onGenerateFromText: vi.fn(),
    onGenerateFromAudio: vi.fn(),
    busy: null,
    ...overrides,
  };
  render(<InputPanel {...props} />);
  return props;
}

describe("InputPanel", () => {
  it("disables generation until the feature input has content", () => {
    const props = renderPanel();
    expect(
      screen.getByRole("button", { name: "Generate user story" }),
    ).toBeDisabled();

    fireEvent.change(screen.getByRole("textbox"), {
      target: { value: "As a shopper, I want a wishlist" },
    });
    expect(props.onFeatureChange).toHaveBeenCalledWith(
      "As a shopper, I want a wishlist",
    );
  });

  it("fires the text generation callback", () => {
    const props = renderPanel({ feature: "a feature" });
    fireEvent.click(screen.getByRole("button", { name: "Generate user story" }));
    expect(props.onGenerateFromText).toHaveBeenCalledOnce();
  });

  it("fills the input when a sample prompt is clicked", () => {
    const props = renderPanel();
    const [sample] = screen.getAllByRole("button", {
      name: /save items to a wishlist/i,
    });
    fireEvent.click(sample);
    expect(props.onFeatureChange).toHaveBeenCalledWith(
      expect.stringContaining("save items to a wishlist"),
    );
  });

  it("supports Ctrl+Enter as a generate shortcut", () => {
    const props = renderPanel({ feature: "a feature" });
    fireEvent.keyDown(screen.getByRole("textbox"), {
      key: "Enter",
      ctrlKey: true,
    });
    expect(props.onGenerateFromText).toHaveBeenCalledOnce();
  });

  it("locks the controls and shows progress while generating", () => {
    renderPanel({ feature: "a feature", busy: "text" });
    expect(screen.getByRole("button", { name: /generating/i })).toBeDisabled();
    expect(screen.getByRole("button", { name: /save items to a wishlist/i })).toBeDisabled();
  });

  it("reports the selected audio file and stays disabled without one", () => {
    const props = renderPanel();
    const audioButton = screen.getByRole("button", {
      name: "Transcribe & generate",
    });
    expect(audioButton).toBeDisabled();

    const file = new File(["x"], "note.wav", { type: "audio/wav" });
    fireEvent.change(screen.getByTestId("audio-input"), {
      target: { files: [file] },
    });
    expect(props.onAudioFileChange).toHaveBeenCalledWith(file);
  });

  it("fires the audio generation callback once a file is selected", () => {
    const props = renderPanel({
      audioFile: new File(["x"], "note.wav", { type: "audio/wav" }),
    });
    fireEvent.click(
      screen.getByRole("button", { name: "Transcribe & generate" }),
    );
    expect(props.onGenerateFromAudio).toHaveBeenCalledOnce();
  });
});
