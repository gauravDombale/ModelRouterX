import pytest

from gateway.routing.classifier import TaskClassifier
from gateway.schemas import ChatMessage


@pytest.mark.asyncio
async def test_classifier_detects_code():
    classifier = TaskClassifier()
    task, confidence = await classifier.classify([ChatMessage(role="user", content="Write a Python function for binary search")])
    assert task == "code"
    assert confidence > 0

