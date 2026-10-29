import type { ComponentProps } from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import OutputPanel from "./OutputPanel";

type Props = ComponentProps<typeof OutputPanel>;

const STORY = "## User Story\n\nAs a shopper, I want a wishlist.";

function renderPanel(overrides: Partial<Props> = {}) {
  const props: Props = {
    story: "",
    transcript: null,
    busy: null,
    error: null,
    onClear: vi.fn(),
    ...overrides,
  };
  render(<OutputPanel {...props} />);
  return props;
}

describe("OutputPanel", () => {
  it("shows an empty state when nothing has been generated", () => {
    renderPanel();
    expect(screen.getByText("No story generated yet")).toBeInTheDocument();
  });

  it("renders the generated story as markdown", () => {
    renderPanel({ story: STORY });
    expect(
      screen.getByRole("heading", { name: "User Story" }),
    ).toBeInTheDocument();
  });

  it("shows the audio transcript when present", () => {
    renderPanel({ story: STORY, transcript: "users want password reset" });
    expect(screen.getByText("users want password reset")).toBeInTheDocument();
  });

  it("surfaces errors", () => {
    renderPanel({ error: "LLM request failed" });
    expect(screen.getByText("LLM request failed")).toBeInTheDocument();
    expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
  });

  it("copies the story to the clipboard", async () => {
    const writeText = vi.fn().mockResolvedValue(undefined);
    Object.defineProperty(navigator, "clipboard", {
      value: { writeText },
      configurable: true,
    });
    renderPanel({ story: STORY });

    fireEvent.click(screen.getByRole("button", { name: "Copy" }));

    expect(writeText).toHaveBeenCalledWith(STORY);
    expect(await screen.findByText("Copied ✓")).toBeInTheDocument();
  });

  it("downloads the story as a markdown file", () => {
    const createObjectURL = vi.fn(() => "blob:story");
    const revokeObjectURL = vi.fn();
    Object.assign(URL, { createObjectURL, revokeObjectURL });
    const clickSpy = vi
      .spyOn(HTMLAnchorElement.prototype, "click")
      .mockImplementation(() => {});
    renderPanel({ story: STORY });

    fireEvent.click(screen.getByRole("button", { name: "Download .md" }));

    expect(createObjectURL).toHaveBeenCalledOnce();
    expect(clickSpy).toHaveBeenCalledOnce();
    clickSpy.mockRestore();
  });

  it("clears the panel on request", async () => {
    const props = renderPanel({ story: STORY });
    fireEvent.click(screen.getByRole("button", { name: "Clear" }));
    await waitFor(() => expect(props.onClear).toHaveBeenCalledOnce());
  });

  it("only shows the story actions when a story exists", () => {
    renderPanel();
    expect(screen.queryByRole("button", { name: "Copy" })).toBeNull();
    expect(screen.queryByRole("button", { name: "Clear" })).toBeNull();
  });
});
