from __future__ import annotations

import re

from .models import Persona, RetrievedChunk, Turn


SENSITIVE_PATTERN = re.compile(
    r"\b(billing|charged|refund|invoice|legal|lawsuit|attorney|account owner|"
    r"delete my account|identity|fraud|security breach|personal data)\b",
    re.IGNORECASE,
)
DISSATISFIED_PATTERN = re.compile(
    r"\b(still|again|did not work|doesn't work|not fixed|useless|nothing works)\b",
    re.IGNORECASE,
)


class EscalationPolicy:
    def __init__(self, retrieval_threshold: float, dissatisfaction_turns: int):
        self.retrieval_threshold = retrieval_threshold
        self.dissatisfaction_turns = dissatisfaction_turns

    def evaluate(self, message: str, retrieved: list[RetrievedChunk], history: list[Turn]) -> list[str]:
        reasons: list[str] = []
        if not retrieved:
            reasons.append("No relevant knowledge-base content was found")
        elif retrieved[0].score < self.retrieval_threshold:
            reasons.append(f"Retrieval confidence is low ({retrieved[0].score:.2f})")
        if SENSITIVE_PATTERN.search(message):
            reasons.append("Billing, legal, security, or account-sensitive issue")
        dissatisfaction = sum(bool(DISSATISFIED_PATTERN.search(t.user)) for t in history[-4:])
        dissatisfaction += bool(DISSATISFIED_PATTERN.search(message))
        if dissatisfaction >= self.dissatisfaction_turns:
            reasons.append("User remains dissatisfied across multiple interactions")
        return reasons


def build_handoff(
    persona: Persona,
    message: str,
    history: list[Turn],
    retrieved: list[RetrievedChunk],
    reasons: list[str],
) -> dict:
    attempted = [turn.assistant[:240] for turn in history if turn.assistant]
    return {
        "persona": persona.value,
        "issue": message,
        "conversation_history": [{"user": t.user, "assistant": t.assistant} for t in history],
        "documents_used": list(dict.fromkeys(item.chunk.citation for item in retrieved)),
        "actions_already_attempted": attempted,
        "escalation_reasons": reasons,
        "recommended_next_steps": "Human agent should verify the account context, review attempted steps, and contact the user.",
    }

