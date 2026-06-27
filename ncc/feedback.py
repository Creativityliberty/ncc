from __future__ import annotations

from .schemas import Feedback


def no_feedback() -> Feedback:
    return Feedback(type="none", content="", impact={})


def correction_feedback(content: str) -> Feedback:
    return Feedback(type="correction", content=content, impact={"intent": 0.7, "memory": 0.5, "policy": 0.2})


from ncc.schemas import FeedbackRecord

def extract_feedback(user_input: str, source_step: int | None = None) -> FeedbackRecord | None:
    text = user_input.lower()

    feedback_markers = [
        "à partir de maintenant",
        "a partir de maintenant",
        "désormais",
        "desormais",
        "ne fais plus",
        "il faut toujours",
        "dorénavant",
        "corrige",
        "garde ça",
        "retiens",
    ]

    if not any(marker in text for marker in feedback_markers):
        return None

    derived_policy_rules = []
    derived_constraints = []
    feedback_type = "correction"
    scope = "task"

    if "sauvegarde" in text and ("confirmation" in text or "confirmer" in text):
        derived_policy_rules.append(
            "destructive_actions_require_backup_and_confirmation"
        )
        derived_constraints.append("require_backup_before_destructive_action")
        derived_constraints.append("require_confirmation_before_destructive_action")
        feedback_type = "policy_update"
        scope = "safety"

    return FeedbackRecord(
        content=user_input,
        feedback_type=feedback_type,
        scope=scope,
        derived_constraints=derived_constraints,
        derived_policy_rules=derived_policy_rules,
        source_step=source_step,
        salience=0.9,
    )


def consolidate_feedback(state, feedback_record: FeedbackRecord):
    state.feedback_records.append(feedback_record)

    for rule in feedback_record.derived_policy_rules:
        if rule not in state.learned_policy_rules:
            state.learned_policy_rules.append(rule)

    return state
