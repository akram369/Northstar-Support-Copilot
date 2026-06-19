from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class Settings:
    data_dir: Path = Path("data")
    index_path: Path = Path(".support_index.sqlite3")
    top_k: int = 4
    chunk_size: int = 850
    chunk_overlap: int = 120
    retrieval_threshold: float = 0.15
    dissatisfaction_turns: int = 2
    llm_provider: str = "template"
    openai_model: str = "gpt-4o-mini"
    gemini_model: str = "gemini-2.5-flash"
    ollama_model: str = "llama3.2"
    ollama_base_url: str = "http://localhost:11434"

    @classmethod
    def from_env(cls, project_root: Path | None = None) -> "Settings":
        root = project_root or Path.cwd()
        try:
            from dotenv import load_dotenv

            env_path = root / ".env"
            print(f"DEBUG: Loading dotenv from {env_path}, exists: {env_path.exists()}")
            load_dotenv(env_path, override=True)
            print(f"DEBUG: LLM_PROVIDER after dotenv: {os.getenv('LLM_PROVIDER')}")
        except ImportError:
            print("DEBUG: dotenv not installed")
        return cls(
            data_dir=root / os.getenv("DATA_DIR", "data"),
            index_path=root / os.getenv("INDEX_PATH", ".support_index.sqlite3"),
            top_k=int(os.getenv("TOP_K", "4")),
            chunk_size=int(os.getenv("CHUNK_SIZE", "850")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "120")),
            retrieval_threshold=float(os.getenv("RETRIEVAL_THRESHOLD", "0.08")),
            dissatisfaction_turns=int(os.getenv("DISSATISFACTION_TURNS", "2")),
            llm_provider=os.getenv("LLM_PROVIDER", "template").lower(),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            gemini_model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"),
            ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2"),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )
