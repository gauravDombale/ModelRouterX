from gateway.schemas import ChatMessage


def _content_to_text(content: str | list[dict]) -> str:
    if isinstance(content, str):
        return content
    return " ".join(str(part.get("text", part)) for part in content)


def count_message_tokens(messages: list[ChatMessage] | list[dict]) -> int:
    chars = 0
    for message in messages:
        content = message.content if hasattr(message, "content") else message.get("content", "")
        chars += len(_content_to_text(content))
    return max(1, chars // 4)


def count_text_tokens(text: str) -> int:
    return max(1, len(text) // 4)

