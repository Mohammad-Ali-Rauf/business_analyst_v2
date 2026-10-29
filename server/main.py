"""FastAPI service exposing user-story generation from text and audio."""

from __future__ import annotations

import logging
import os
import tempfile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from agents.user_story_agent import StoryGenerationError, generate_user_story
from config import ALLOWED_ORIGINS, MAX_AUDIO_BYTES
from utils.audio_to_text import transcribe_audio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("server")

app = FastAPI(
    title="Agile User Story Generator API",
    version="2.0.0",
    description=(
        "Generates structured agile user stories (with context, acceptance "
        "criteria, security requirements and test scenarios) from typed "
        "feature descriptions or uploaded audio notes."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    # Wildcard origins and credentials cannot be combined per the CORS spec.
    allow_credentials="*" not in ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


@app.post("/generate_from_text")
async def generate_from_text(text: str = Form(...), token: str = Form(...)) -> dict:
    """Generate a user story from a typed feature description."""
    if not text.strip():
        raise HTTPException(status_code=422, detail="'text' must not be empty")
    if not token.strip():
        raise HTTPException(status_code=422, detail="'token' must not be empty")

    try:
        story = generate_user_story(text, token)
    except StoryGenerationError as exc:
        logger.warning("Story generation failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {"story": story}


@app.post("/generate_from_audio")
async def generate_from_audio(
    file: UploadFile = File(...),
    token: str = Form(...),
) -> dict:
    """Transcribe an audio note, then generate a user story from it."""
    if not token.strip():
        raise HTTPException(status_code=422, detail="'token' must not be empty")

    audio = await file.read()
    if not audio:
        raise HTTPException(status_code=422, detail="Uploaded file is empty")
    if len(audio) > MAX_AUDIO_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Audio file exceeds the {MAX_AUDIO_BYTES // (1024 * 1024)} MB limit",
        )

    suffix = os.path.splitext(file.filename or "")[1] or ".wav"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=True) as tmp:
        tmp.write(audio)
        tmp.flush()
        try:
            transcription = transcribe_audio(tmp.name)
        except Exception as exc:
            logger.exception("Transcription failed")
            raise HTTPException(status_code=422, detail=f"Transcription failed: {exc}") from exc

    if not transcription:
        raise HTTPException(status_code=422, detail="No speech detected in the audio")

    try:
        story = generate_user_story(transcription, token)
    except StoryGenerationError as exc:
        logger.warning("Story generation failed: %s", exc)
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {"transcription": transcription, "story": story}
