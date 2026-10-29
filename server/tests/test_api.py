"""Endpoint behaviour: health check and input validation errors."""

from __future__ import annotations

import main


def test_health_returns_ok(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_generate_from_text_rejects_empty_text(client, llm_stub):
    response = client.post(
        "/generate_from_text", data={"text": "   ", "token": "session-1"}
    )
    assert response.status_code == 422


def test_generate_from_text_rejects_empty_token(client, llm_stub):
    response = client.post(
        "/generate_from_text", data={"text": "a feature", "token": " "}
    )
    assert response.status_code == 422


def test_generate_from_audio_rejects_empty_token(client, llm_stub):
    response = client.post(
        "/generate_from_audio",
        files={"file": ("note.wav", b"RIFFdata", "audio/wav")},
        data={"token": ""},
    )
    assert response.status_code == 422


def test_generate_from_audio_rejects_empty_file(client, llm_stub):
    response = client.post(
        "/generate_from_audio",
        files={"file": ("note.wav", b"", "audio/wav")},
        data={"token": "session-1"},
    )
    assert response.status_code == 422


def test_generate_from_audio_rejects_oversized_file(client, llm_stub, monkeypatch):
    monkeypatch.setattr(main, "MAX_AUDIO_BYTES", 8)
    response = client.post(
        "/generate_from_audio",
        files={"file": ("note.wav", b"0123456789", "audio/wav")},
        data={"token": "session-1"},
    )
    assert response.status_code == 413


def test_generate_from_audio_rejects_unintelligible_audio(client, llm_stub, monkeypatch):
    monkeypatch.setattr(main, "transcribe_audio", lambda path: "")
    response = client.post(
        "/generate_from_audio",
        files={"file": ("note.wav", b"RIFFdata", "audio/wav")},
        data={"token": "session-1"},
    )
    assert response.status_code == 422


def test_generate_from_audio_maps_transcription_failure(client, llm_stub, monkeypatch):
    def boom(path: str) -> str:
        raise RuntimeError("ffmpeg exploded")

    monkeypatch.setattr(main, "transcribe_audio", boom)
    response = client.post(
        "/generate_from_audio",
        files={"file": ("note.wav", b"RIFFdata", "audio/wav")},
        data={"token": "session-1"},
    )
    assert response.status_code == 422
    assert "Transcription failed" in response.json()["detail"]
