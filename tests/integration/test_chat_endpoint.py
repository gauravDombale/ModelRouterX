import pytest

from gateway.schemas import ChatCompletionRequest, ChatMessage


@pytest.mark.asyncio
async def test_chat_request_schema_accepts_openai_shape():
    payload = ChatCompletionRequest(model="auto", messages=[ChatMessage(role="user", content="Hello")])
    assert payload.model == "auto"
    assert payload.messages[0].role == "user"

