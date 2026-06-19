from __future__ import annotations

import re

from .models import Persona


TECHNICAL_TERMS = {
    "api", "sdk", "http", "json", "oauth", "token", "webhook", "endpoint",
    "latency", "logs", "stack trace", "status code", "configuration", "cli",
    "database", "timeout", "exception", "authentication", "rate limit",
}
FRUSTRATION_TERMS = {
    "frustrated", "angry", "ridiculous", "unacceptable", "nothing works",
    "again", "still broken", "urgent", "immediately", "terrible", "fed up",
    "tried everything", "waste", "!!!", "asap",
}
EXECUTIVE_TERMS = {
    "business impact", "operations", "revenue", "sla", "timeline", "eta",
    "executive", "customers affected", "risk", "priority", "downtime", "roi",
    "when will", "summary", "bottom line", "compliance",
}


class PersonaDetector:
    """Transparent weighted classifier suitable for auditable support routing."""

    def detect(self, message: str) -> tuple[Persona, float, dict[str, float]]:
        text = message.lower()
        scores = {
            Persona.TECHNICAL_EXPERT: self._score(text, TECHNICAL_TERMS),
            Persona.FRUSTRATED_USER: self._score(text, FRUSTRATION_TERMS),
            Persona.BUSINESS_EXECUTIVE: self._score(text, EXECUTIVE_TERMS),
        }
        if re.search(r"\b(4\d\d|5\d\d)\b|[{}]|--[a-z-]+", text):
            scores[Persona.TECHNICAL_EXPERT] += 2.0
        if text.count("!") >= 2 or text.isupper():
            scores[Persona.FRUSTRATED_USER] += 2.0
        if len(message.split()) <= 18 and any(x in text for x in ("impact", "eta", "timeline")):
            scores[Persona.BUSINESS_EXECUTIVE] += 1.5

        winner = max(scores, key=scores.get)
        total = sum(scores.values())
        if total == 0:
            winner = Persona.BUSINESS_EXECUTIVE
            confidence = 0.55
        else:
            confidence = min(0.98, 0.55 + scores[winner] / (2 * total + 1))
        return winner, round(confidence, 2), {p.value: round(s, 2) for p, s in scores.items()}

    @staticmethod
    def _score(text: str, terms: set[str]) -> float:
        return float(sum(1.0 + (0.35 if " " in term else 0.0) for term in terms if term in text))

