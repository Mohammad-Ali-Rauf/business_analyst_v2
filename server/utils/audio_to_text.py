"""Speech-to-text helper built on OpenAI Whisper.

The Whisper model is heavyweight, so it is loaded lazily on the first
transcription request and cached for the lifetime of the process.
"""

from __future__ import annotations

import logging
import threading

from config import WHISPER_MODEL

logger = logging.getLogger(__name__)

_model = None
_model_lock = threading.Lock()


def _get_model():
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:
                # Imported lazily: importing whisper pulls in torch.
                import whisper

                logger.info("Loading Whisper model %s", WHISPER_MODEL)
                _model = whisper.load_model(WHISPER_MODEL)
    return _model


def transcribe_audio(file_path: str) -> str:
    """Transcribe an audio file and return the plain-text transcript."""
    result = _get_model().transcribe(file_path)
    return str(result.get("text", "")).strip()
