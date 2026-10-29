"""User-story generation agent.

Turns a free-form feature description (typed or transcribed from audio) into a
structured agile user-story document, taking the session's recent history into
account so follow-up requests build on earlier stories.
"""

from __future__ import annotations

import logging
import re

from langchain_core.prompts import PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from config import GEMINI_API_KEY, GEMINI_MODEL, LLM_TEMPERATURE, MEMORY_TOP_K
from utils.memory_manager import get_last_n_memories, save_memory_for_token

logger = logging.getLogger(__name__)

PROMPT_TEMPLATE = PromptTemplate.from_template(
    """You are an expert Agile Product Owner and Business Analyst.

Below is the conversation so far (if any), followed by a new feature request.

---

**Previous Context:**
{history}

---

**New Feature Input:**
{feature_input}

---

Write a user-story document for the new input. Take any relevant prior context
into account: if this story builds on an earlier one, reference it naturally.

Return ONLY the document in Markdown, using exactly this structure:

## User Story

As a [actor],
I want to [action],
So that [benefit].

## Context

2-3 lines of background covering the business value, technical considerations,
or UX importance of the story.

## Acceptance Criteria

- Clear
- Testable
- Functional requirements only

## Security Requirements

- Access control, verification, rate limits, etc. (omit this section when the
  story has no security implications)

## Test Scenarios

- Simple bullet-style test cases covering the happy path and edge cases

Do NOT add explanations, commentary, or code fences around the document.
"""
)

_CODE_FENCE_RE = re.compile(r"\A```[a-zA-Z]*\n?|\n?```\Z")


class StoryGenerationError(RuntimeError):
    """Raised when the LLM does not return a usable document."""


def _extract_text(response) -> str:
    """Best-effort extraction of the message text from an LLM response."""
    content = getattr(response, "content", None)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        # Newer model responses may return a list of content blocks.
        return "\n".join(
            block.get("text", "") if isinstance(block, dict) else str(block)
            for block in content
        )
    if isinstance(response, dict) and "text" in response:
        return str(response["text"])
    return str(response)


def generate_user_story(feature_input: str, token: str) -> str:
    """Generate a Markdown user-story document for ``feature_input``.

    The input and the generated document are both stored in session memory so
    the next request can reference them.
    """
    feature_input = feature_input.strip()
    if not feature_input:
        raise ValueError("feature_input must not be empty")
    if not GEMINI_API_KEY:
        raise StoryGenerationError("GEMINI_API_KEY is not configured on the server")

    history = get_last_n_memories(token, n=MEMORY_TOP_K)
    history_text = "\n".join(history) if history else "No prior context available."

    prompt = PROMPT_TEMPLATE.format(
        history=history_text,
        feature_input=feature_input,
    )

    llm = ChatGoogleGenerativeAI(
        model=GEMINI_MODEL,
        api_key=GEMINI_API_KEY,
        temperature=LLM_TEMPERATURE,
    )

    try:
        response = llm.invoke(prompt)
    except Exception as exc:
        logger.exception("LLM call failed for session %s", token)
        raise StoryGenerationError(f"LLM request failed: {exc}") from exc

    document = _CODE_FENCE_RE.sub("", _extract_text(response)).strip()
    if not document:
        raise StoryGenerationError("LLM returned an empty document")

    save_memory_for_token(token, feature_input, role="user")
    save_memory_for_token(token, document, role="assistant")

    return document
