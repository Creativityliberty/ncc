from __future__ import annotations

from .schemas import Feedback


def no_feedback() -> Feedback:
    return Feedback(type="none", content="", impact={})


def correction_feedback(content: str) -> Feedback:
    return Feedback(type="correction", content=content, impact={"intent": 0.7, "memory": 0.5, "policy": 0.2})
