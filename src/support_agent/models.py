from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class Persona(str, Enum):
    TECHNICAL_EXPERT = "Technical Expert"
    FRUSTRATED_USER = "Frustrated User"
    BUSINESS_EXECUTIVE = "Business Executive"


@dataclass(slots=True)
class DocumentChunk:
    id: str
    text: str
    source: str
    section: str
    page: int | None = None

    @property
    def citation(self) -> str:
        location = f"page {self.page}" if self.page else self.section
        return f"{self.source} ({location})"


@dataclass(slots=True)
class RetrievedChunk:
    chunk: DocumentChunk
    score: float


@dataclass(slots=True)
class Turn:
    user: str
    assistant: str
    persona: Persona
    sources: list[str] = field(default_factory=list)
    escalated: bool = False


@dataclass(slots=True)
class AgentResponse:
    response: str
    persona: Persona
    persona_confidence: float
    retrieved: list[RetrievedChunk]
    escalation_status: bool
    escalation_reasons: list[str]
    handoff_summary: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        result = asdict(self)
        result["persona"] = self.persona.value
        return result

