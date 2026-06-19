from support_agent.models import Persona
from support_agent.persona import PersonaDetector


def test_detects_technical_expert():
    persona, confidence, scores = PersonaDetector().detect(
        "The API returns HTTP 401 invalid_token. Can you explain the OAuth configuration and logs?"
    )
    assert persona is Persona.TECHNICAL_EXPERT
    assert confidence >= 0.6
    assert scores[Persona.TECHNICAL_EXPERT.value] > 0


def test_detects_frustrated_user():
    persona, _, _ = PersonaDetector().detect("I have tried everything and nothing works!!! This is ridiculous.")
    assert persona is Persona.FRUSTRATED_USER


def test_detects_executive():
    persona, _, _ = PersonaDetector().detect("What is the business impact, risk, and timeline for operations?")
    assert persona is Persona.BUSINESS_EXECUTIVE

