from support_agent.escalation import EscalationPolicy
from support_agent.models import DocumentChunk, RetrievedChunk, Turn, Persona


def result(score: float):
    return [RetrievedChunk(DocumentChunk("1", "context", "source.md", "section"), score)]


def test_low_confidence_escalates():
    reasons = EscalationPolicy(0.2, 2).evaluate("Help with this", result(0.05), [])
    assert any("confidence" in reason for reason in reasons)


def test_sensitive_issue_escalates():
    reasons = EscalationPolicy(0.1, 2).evaluate("I was charged twice and need a refund", result(0.8), [])
    assert any("sensitive" in reason for reason in reasons)


def test_repeated_dissatisfaction_escalates():
    history = [Turn("It still does not work", "Try this", Persona.FRUSTRATED_USER)]
    reasons = EscalationPolicy(0.1, 2).evaluate("Again, nothing works", result(0.8), history)
    assert any("dissatisfied" in reason for reason in reasons)

