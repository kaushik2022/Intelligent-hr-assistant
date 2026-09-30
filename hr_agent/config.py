"""
hr_agent/config.py
Configuration parameters for the Google ADK Intelligent HR Assistant Agent.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from dotenv import load_dotenv

BASE_DIR = Path(__file__).parent.parent
# Load .env file automatically
load_dotenv(BASE_DIR / ".env")

@dataclass
class HRConfig:
    docs_dir: Path = BASE_DIR / "documents"
    chroma_db_dir: Path = BASE_DIR / "chroma_db"
    collection_name: str = "hr_company_policies"
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY", ""))
    model_name: str = os.getenv("HR_AGENT_MODEL", "gemini-2.5-flash")
    chunk_size: int = 600
    chunk_overlap: int = 100
    top_k_results: int = 3

config = HRConfig()
