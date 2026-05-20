from gateway.models.routing_rule import RoutingRule
from gateway.schemas import ChatCompletionRequest


def _request_text(request: ChatCompletionRequest) -> str:
    return "\n".join(str(m.content) for m in request.messages).lower()


def rule_matches(rule: RoutingRule, request: ChatCompletionRequest, task_type: str) -> bool:
    conditions = rule.conditions or {}
    text = _request_text(request)
    contains = conditions.get("prompt_contains")
    if contains and not any(str(term).lower() in text for term in contains):
        return False
    if conditions.get("task_type") and conditions["task_type"] != task_type:
        return False
    if conditions.get("max_tokens_gt") is not None and (request.max_tokens or 0) <= int(conditions["max_tokens_gt"]):
        return False
    return True


def choose_rule_based(rules: list[RoutingRule], request: ChatCompletionRequest, task_type: str) -> tuple[str, str] | None:
    for rule in sorted((r for r in rules if r.is_active), key=lambda r: r.priority, reverse=True):
        if rule_matches(rule, request, task_type):
            return rule.target_model, f"Matched rule: {rule.name}"
    return None

