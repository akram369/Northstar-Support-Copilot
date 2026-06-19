from __future__ import annotations

import json
import os
import urllib.request
from typing import Protocol

from .models import Persona, RetrievedChunk, Turn


PERSONA_INSTRUCTIONS = {
    Persona.TECHNICAL_EXPERT: (
        "Use precise technical language. Explain the likely cause, numbered diagnostic steps, "
        "and relevant configuration or error details. Do not invent facts."
    ),
    Persona.FRUSTRATED_USER: (
        "Acknowledge the frustration briefly, use plain reassuring language, and give a short, "
        "action-oriented sequence. Do not blame the user."
    ),
    Persona.BUSINESS_EXECUTIVE: (
        "Be concise and outcome-focused. State operational impact and documented resolution "
        "guidance without unnecessary implementation detail."
    ),
}


class ResponseGenerator(Protocol):
    def generate(self, message: str, persona: Persona, retrieved: list[RetrievedChunk], history: list[Turn]) -> str: ...


def build_prompt(message: str, persona: Persona, retrieved: list[RetrievedChunk], history: list[Turn]) -> str:
    context = "\n\n".join(
        f"SOURCE [{i}] {item.chunk.citation}\n{item.chunk.text}"
        for i, item in enumerate(retrieved, start=1)
    )
    recent = "\n".join(f"User: {t.user}\nAssistant: {t.assistant}" for t in history[-3:]) or "None"
    return f"""You are a customer support agent. Answer ONLY with facts present in CONTEXT.
If the context is insufficient, say that a human specialist is needed. Never invent an ETA.

PERSONA: {persona.value}
STYLE: {PERSONA_INSTRUCTIONS[persona]}

RECENT CONVERSATION:
{recent}

CONTEXT:
{context}

USER MESSAGE:
{message}

Write the answer with inline source markers such as [1]."""


class OpenAIGenerator:
    def __init__(self, model: str):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("Install the 'openai' package to use LLM_PROVIDER=openai") from exc
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        self.model = model

    def generate(self, message: str, persona: Persona, retrieved: list[RetrievedChunk], history: list[Turn]) -> str:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": build_prompt(message, persona, retrieved, history)}],
                temperature=0.2,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"⚠️ OpenAI API Error: {str(e)}. Please check your API key quota or billing."


class GeminiGenerator:
    def __init__(self, model: str):
        try:
            from google import genai
        except ImportError as exc:
            raise RuntimeError("Install 'google-genai' package to use LLM_PROVIDER=gemini") from exc
        
        self.client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        self.model = model

    def generate(self, message: str, persona: Persona, retrieved: list[RetrievedChunk], history: list[Turn]) -> str:
        try:
            from google.genai import types
            print("DEBUG: GeminiGenerator.generate IS BEING CALLED")
            response = self.client.models.generate_content(
                model=self.model,
                contents=build_prompt(message, persona, retrieved, history),
                config=types.GenerateContentConfig(temperature=0.2)
            )
            print("DEBUG: Gemini response text:", response.text)
            return response.text.strip()
        except Exception as e:
            return f"⚠️ Gemini API Error: {str(e)}. Please verify your GEMINI_API_KEY."


class OllamaGenerator:
    def __init__(self, model: str, base_url: str):
        self.model = model
        self.base_url = base_url.rstrip("/")

    def generate(self, message: str, persona: Persona, retrieved: list[RetrievedChunk], history: list[Turn]) -> str:
        import json
        import urllib.request

        req = urllib.request.Request(
            f"{self.base_url}/api/generate",
            data=json.dumps(
                {
                    "model": self.model,
                    "prompt": build_prompt(message, persona, retrieved, history),
                    "stream": False,
                    "options": {"temperature": 0.2},
                }
            ).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req) as response:
                return json.loads(response.read().decode("utf-8"))["response"].strip()
        except Exception as e:
            return f"⚠️ Ollama Connection Error: {str(e)}. Ensure Ollama is running locally."


class GroundedTemplateGenerator:
    """Offline, extractive fallback. It composes only retrieved support text."""

    def generate(self, message: str, persona: Persona, retrieved: list[RetrievedChunk], history: list[Turn]) -> str:
        if not retrieved:
            return "I could not find verified guidance for this issue. I will route it to a human specialist."
        facts = [self._clean(item.chunk.text) for item in retrieved[:2]]
        if persona is Persona.FRUSTRATED_USER:
            lead = "I’m sorry this has been such a hassle. Here’s the clearest path forward:"
            body = "\n".join(f"{i}. {fact} [{i}]" for i, fact in enumerate(facts, 1))
            return f"{lead}\n\n{body}"
        if persona is Persona.TECHNICAL_EXPERT:
            body = "\n".join(f"{i}. {fact} [{i}]" for i, fact in enumerate(facts, 1))
            return f"Based on the documented behavior, use this diagnostic sequence:\n\n{body}"
        return f"Documented guidance: {facts[0]} [1]" + (f"\n\nNext step: {facts[1]} [2]" if len(facts) > 1 else "")

    @staticmethod
    def _clean(text: str) -> str:
        lines = [line.strip(" -*") for line in text.splitlines() if line.strip()]
        value = " ".join(lines)
        return value[:550].rstrip() + ("…" if len(value) > 550 else "")


def create_generator(provider: str, openai_model: str, gemini_model: str, ollama_model: str, ollama_base_url: str) -> ResponseGenerator:
    if provider == "openai":
        return OpenAIGenerator(openai_model)
    if provider == "gemini":
        return GeminiGenerator(gemini_model)
    if provider == "ollama":
        return OllamaGenerator(ollama_model, ollama_base_url)
    return GroundedTemplateGenerator()

