"""Shared fixtures for the API test-suite.

The LLM client and the session memory are stubbed so the suite runs fully
offline and without an API key.
"""

from __future__ import annotations

import pathlib
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from fastapi.testclient import TestClient  # noqa: E402

import agents.user_story_agent as agent  # noqa: E402
import main  # noqa: E402

SAMPLE_STORY = (
    "## User Story\n\n"
    "As a shopper,\n"
    "I want to save items to a wishlist,\n"
    "So that I can buy them later."
)


@pytest.fixture()
def client() -> TestClient:
    return TestClient(main.app)


@pytest.fixture()
def llm_stub(monkeypatch: pytest.MonkeyPatch) -> SimpleNamespace:
    """Replace the chat model and session memory with in-process stubs.

    Returns a namespace exposing the captured calls so tests can assert on
    the prompt and the stored memories.
    """
    calls: list[SimpleNamespace] = []
    saved: list[tuple[str, str]] = []

    class FakeLLM:
        def __init__(self, **kwargs: object) -> None:
            self.init_kwargs = kwargs
            self.prompt: str | None = None
            calls.append(self)

        def invoke(self, prompt: str) -> SimpleNamespace:
            self.prompt = prompt
            return SimpleNamespace(content=SAMPLE_STORY)

    monkeypatch.setattr(agent, "ChatOpenAI", FakeLLM)
    monkeypatch.setattr(agent, "LLM_API_KEY", "test-key")
    monkeypatch.setattr(agent, "get_last_n_memories", lambda token, n: [])
    monkeypatch.setattr(
        agent,
        "save_memory_for_token",
        lambda token, text, role="assistant": saved.append((role, text)),
    )
    return SimpleNamespace(calls=calls, saved=saved, FakeLLM=FakeLLM)
