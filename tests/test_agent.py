from pathlib import Path

from support_agent.agent import SupportAgent
from support_agent.config import Settings


def test_agent_end_to_end(tmp_path: Path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "api.md").write_text(
        "# Authentication\nA 401 invalid_token means a token is expired, malformed, or revoked.",
        encoding="utf-8",
    )
    settings = Settings(data_dir=data, index_path=tmp_path / "index.sqlite3", retrieval_threshold=0.01)
    agent = SupportAgent(settings)
    assert agent.ingest() == 1
    response = agent.ask("The API returns 401 invalid_token. Show technical troubleshooting.")
    assert response.persona.value == "Technical Expert"
    assert response.retrieved[0].chunk.source == "api.md"
    assert "401" in response.response
    agent.close()


def test_response_based_escalation_triggers(tmp_path: Path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "api.md").write_text(
        "# Authentication\nSome text.",
        encoding="utf-8",
    )
    settings = Settings(data_dir=data, index_path=tmp_path / "index.sqlite3", retrieval_threshold=0.01)
    agent = SupportAgent(settings)
    assert agent.ingest() == 1

    # Mock the generator to return a message indicating a human specialist is needed
    class MockGenerator:
        def generate(self, message, persona, retrieved, history):
            return "A human specialist is needed to look at this."

    agent.generator = MockGenerator()

    response = agent.ask("Some query")
    assert response.escalation_status is True
    assert "human specialist" in response.response
    assert any("human specialist" in r.lower() for r in response.escalation_reasons)
    assert response.handoff_summary is not None
    agent.close()
