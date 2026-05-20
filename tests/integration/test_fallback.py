from gateway.routing.fallback import fallback_chain


def test_fallback_chain_is_deduped_and_includes_primary():
    chain = fallback_chain("claude-sonnet-4-20250514", ["gpt-4o-2024-11-20"])
    assert chain[0] == "claude-sonnet-4-20250514"
    assert len(chain) == len(set(chain))

