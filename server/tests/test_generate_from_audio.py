"""Transcription + generation flow for /generate_from_audio."""

from __future__ import annotations

import agents.user_story_agent as agent
import main
from tests.conftest import SAMPLE_STORY


def test_audio_flows_through_transcription_into_the_story(
    client, llm_stub, monkeypatch
):
    monkeypatch.setattr(
        main, "transcribe_audio", lambda path: "Users want password reset by email"
    )
    response = client.post(
        "/generate_from_audio",
        files={"file": ("note.wav", b"RIFFdata", "audio/wav")},
        data={"token": "session-1"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "transcription": "Users want password reset by email",
        "story": SAMPLE_STORY,
    }
    # The transcription is what reaches the agent.
    assert llm_stub.saved[0] == ("user", "Users want password reset by email")


def test_audio_generation_failure_returns_502(client, llm_stub, monkeypatch):
    monkeypatch.setattr(main, "transcribe_audio", lambda path: "a feature")

    class ExplodingLLM(llm_stub.FakeLLM):
        def invoke(self, prompt: str):
            raise ConnectionError("upstream unavailable")

    monkeypatch.setattr(agent, "ChatOpenAI", ExplodingLLM)
    response = client.post(
        "/generate_from_audio",
        files={"file": ("note.wav", b"RIFFdata", "audio/wav")},
        data={"token": "session-1"},
    )
    assert response.status_code == 502
