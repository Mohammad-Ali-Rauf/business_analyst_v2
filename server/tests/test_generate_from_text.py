"""Happy paths and LLM failure handling for /generate_from_text."""

from __future__ import annotations

import pytest

import agents.user_story_agent as agent
from tests.conftest import SAMPLE_STORY


def test_success_returns_markdown_story(client, llm_stub):
    response = client.post(
        "/generate_from_text",
        data={"text": "As a shopper, I want a wishlist", "token": "session-1"},
    )
    assert response.status_code == 200
    assert response.json() == {"story": SAMPLE_STORY}


def test_success_stores_input_and_story_in_memory(client, llm_stub):
    client.post(
        "/generate_from_text",
        data={"text": "As a shopper, I want a wishlist", "token": "session-1"},
    )
    assert llm_stub.saved == [
        ("user", "As a shopper, I want a wishlist"),
        ("assistant", SAMPLE_STORY),
    ]


def test_history_is_replayed_into_the_prompt(client, llm_stub, monkeypatch):
    monkeypatch.setattr(
        agent,
        "get_last_n_memories",
        lambda token, n: ["Earlier story about wishlists"],
    )
    client.post(
        "/generate_from_text",
        data={"text": "Now add sharing", "token": "session-1"},
    )
    prompt = llm_stub.calls[0].prompt
    assert "Earlier story about wishlists" in prompt
    assert "Now add sharing" in prompt


def test_model_config_is_forwarded_to_the_client(client, llm_stub):
    client.post(
        "/generate_from_text",
        data={"text": "a feature", "token": "session-1"},
    )
    init_kwargs = llm_stub.calls[0].init_kwargs
    assert init_kwargs["api_key"] == "test-key"
    assert init_kwargs["model"] == agent.LLM_MODEL
    assert init_kwargs["base_url"] == agent.LLM_BASE_URL


def test_code_fences_are_stripped_from_the_document(client, llm_stub, monkeypatch):
    class FencedLLM(llm_stub.FakeLLM):
        def invoke(self, prompt: str):
            self.prompt = prompt
            from types import SimpleNamespace

            return SimpleNamespace(content=f"```markdown\n{SAMPLE_STORY}\n```")

    monkeypatch.setattr(agent, "ChatOpenAI", FencedLLM)
    response = client.post(
        "/generate_from_text",
        data={"text": "a feature", "token": "session-1"},
    )
    assert response.json()["story"] == SAMPLE_STORY


def test_missing_api_key_returns_502(client, llm_stub, monkeypatch):
    monkeypatch.setattr(agent, "LLM_API_KEY", "")
    response = client.post(
        "/generate_from_text",
        data={"text": "a feature", "token": "session-1"},
    )
    assert response.status_code == 502
    assert "LLM_API_KEY" in response.json()["detail"]


def test_llm_failure_returns_502(client, llm_stub, monkeypatch):
    class ExplodingLLM(llm_stub.FakeLLM):
        def invoke(self, prompt: str):
            raise ConnectionError("upstream unavailable")

    monkeypatch.setattr(agent, "ChatOpenAI", ExplodingLLM)
    response = client.post(
        "/generate_from_text",
        data={"text": "a feature", "token": "session-1"},
    )
    assert response.status_code == 502
    assert "LLM request failed" in response.json()["detail"]


def test_empty_llm_document_returns_502(client, llm_stub, monkeypatch):
    class EmptyLLM(llm_stub.FakeLLM):
        def invoke(self, prompt: str):
            from types import SimpleNamespace

            return SimpleNamespace(content="   ")

    monkeypatch.setattr(agent, "ChatOpenAI", EmptyLLM)
    response = client.post(
        "/generate_from_text",
        data={"text": "a feature", "token": "session-1"},
    )
    assert response.status_code == 502
    assert "empty document" in response.json()["detail"]


@pytest.mark.parametrize("text", ["plain feature", "  padded feature  "])
def test_input_is_trimmed_before_prompting(client, llm_stub, text):
    client.post("/generate_from_text", data={"text": text, "token": "session-1"})
    stored_user_text = llm_stub.saved[0][1]
    assert stored_user_text == text.strip()
