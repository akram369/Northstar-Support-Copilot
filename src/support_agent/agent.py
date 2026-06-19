from __future__ import annotations

from .config import Settings
from .documents import chunk_documents, load_documents
from .escalation import EscalationPolicy, build_handoff
from .generation import create_generator
from .models import AgentResponse, Turn
from .persona import PersonaDetector
from .vector_store import SQLiteVectorStore


class SupportAgent:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.detector = PersonaDetector()
        self.store = SQLiteVectorStore(settings.index_path)
        self.generator = create_generator(
            settings.llm_provider, settings.openai_model, settings.gemini_model, settings.ollama_model, settings.ollama_base_url
        )
        self.policy = EscalationPolicy(settings.retrieval_threshold, settings.dissatisfaction_turns)
        self.history: list[Turn] = []

    def update_generator(self, provider: str) -> None:
        self.settings.llm_provider = provider
        self.generator = create_generator(
            provider, self.settings.openai_model, self.settings.gemini_model, self.settings.ollama_model, self.settings.ollama_base_url
        )

    def ingest(self) -> int:
        documents = load_documents(self.settings.data_dir)
        chunks = chunk_documents(
            documents, self.settings.data_dir, self.settings.chunk_size, self.settings.chunk_overlap
        )
        if not chunks:
            raise RuntimeError(f"No supported documents found in {self.settings.data_dir}")
        self.store.replace(chunks)
        return len(chunks)

    def ask(self, message: str) -> AgentResponse:
        if not message.strip():
            raise ValueError("Message cannot be empty")
        if self.store.count() == 0:
            self.ingest()
        persona, confidence, _ = self.detector.detect(message)
        retrieved = self.store.search(message, self.settings.top_k)
        reasons = self.policy.evaluate(message, retrieved, self.history)
        response = self.generator.generate(message, persona, retrieved, self.history)
        
        # If the generated response indicates a human specialist is needed, force escalation
        if "human specialist" in response.lower():
            if not reasons:
                reasons = []
            if not any("human specialist" in r.lower() or "insufficient" in r.lower() for r in reasons):
                reasons = list(reasons)
                reasons.append("Grounded response indicated a human specialist is needed")

        handoff = build_handoff(persona, message, self.history, retrieved, reasons) if reasons else None
        turn = Turn(
            user=message,
            assistant=response,
            persona=persona,
            sources=[item.chunk.citation for item in retrieved],
            escalated=bool(reasons),
        )
        self.history.append(turn)
        return AgentResponse(
            response=response,
            persona=persona,
            persona_confidence=confidence,
            retrieved=retrieved,
            escalation_status=bool(reasons),
            escalation_reasons=reasons,
            handoff_summary=handoff,
        )

    def reset(self) -> None:
        self.history.clear()

    def close(self) -> None:
        self.store.close()
