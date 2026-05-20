from gateway.cache.exact_cache import normalize_prompt, prompt_hash
from gateway.schemas import ChatMessage


def test_prompt_normalization_is_user_scoped():
    messages = [
        ChatMessage(role="system", content="You are terse."),
        ChatMessage(role="user", content="  Hello   WORLD "),
    ]
    assert normalize_prompt(messages) == "hello world"
    assert len(prompt_hash(messages)) == 64

