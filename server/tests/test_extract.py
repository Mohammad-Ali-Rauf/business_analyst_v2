"""Unit tests for response text extraction and code-fence cleanup."""

from __future__ import annotations

from types import SimpleNamespace

from agents.user_story_agent import _CODE_FENCE_RE, _extract_text


def test_extract_text_from_message_object():
    assert _extract_text(SimpleNamespace(content="hello")) == "hello"


def test_extract_text_from_content_blocks():
    response = SimpleNamespace(content=[{"text": "part one"}, {"text": "part two"}])
    assert _extract_text(response) == "part one\npart two"


def test_extract_text_from_dict():
    assert _extract_text({"text": "from dict"}) == "from dict"


def test_extract_text_falls_back_to_str():
    assert _extract_text(42) == "42"


def test_code_fence_re_strips_wrapping_fence():
    fenced = "```markdown\n# Story\n```"
    assert _CODE_FENCE_RE.sub("", fenced) == "# Story"


def test_code_fence_re_keeps_inner_content():
    text = "## User Story\n\nAs a user..."
    assert _CODE_FENCE_RE.sub("", text) == text
