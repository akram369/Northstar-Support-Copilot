# Screen Recording Checklist

Target length: about 5 minutes.

## 0:00-0:40 - Project structure

Show the repository tree, the 12 files under `data`, the PDF policy, application modules, tests, and README. Explain that the fictional Northstar SaaS domain keeps retrieval examples consistent.

## 0:40-1:10 - Ingestion

Run:

```bash
python -m support_agent.cli --ingest
```

Explain loading, heading/page metadata, overlapping chunks, local embeddings, and SQLite persistence.

## 1:10-3:20 - Personas and retrieval

Open Streamlit. Ask:

1. `Our API returns 401 invalid_token in production but works in sandbox. What should I verify?`
2. `I've reset my password again and again and NOTHING works!!!`
3. `What is the operational impact of an active incident and when will it be resolved?`
4. `Why does webhook HMAC verification fail after I parse and re-serialize the JSON?`
5. `Summarize the risk and next action for persistent API latency.`

For each, point to the detected persona, source citations, retrieval scores, and different answer style.

## 3:20-4:20 - Escalation and handoff

Ask: `I was charged twice and need an immediate refund.`

Show that billing is always escalated even when relevant documentation is found. Expand the structured handoff and point out conversation history, documents, attempted actions, reasons, and recommendation.

Optionally ask two dissatisfied messages in sequence to demonstrate the configurable multi-turn trigger.

## 4:20-5:00 - Design decision and limitations

Explain that escalation is deterministic and runs outside the LLM, preventing a generated answer from bypassing mandatory policy. Finish by noting that feature hashing is reproducible and offline, while a production deployment would use a semantic embedding service and scalable vector database.

