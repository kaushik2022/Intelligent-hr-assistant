"""
hr_agent/ingest.py
Document Ingestion Pipeline for Intelligent HR Assistant Agent.
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional

from .config import config
from .vector_store import HRVectorStore

def parse_markdown_policy(file_path: Path) -> List[Dict[str, Any]]:
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    filename = file_path.name
    category = filename.replace(".md", "").replace("_policy", "").replace("_", " ").title()
    
    title_match = re.search(r"^#\s+(.+)$", text, re.MULTILINE)
    policy_title = title_match.group(1).strip() if title_match else filename.replace(".md", "")

    doc_id_match = re.search(r"\*\*Document ID:\*\*\s*([A-Z0-9\-]+)", text)
    doc_id = doc_id_match.group(1).strip() if doc_id_match else "POL-HR-GENERAL"

    sections = re.split(r"(^##\s+.+$)", text, flags=re.MULTILINE)
    chunks: List[Dict[str, Any]] = []

    preamble = sections[0].strip()
    if preamble and len(preamble) > 50:
        chunks.append({
            "content": preamble,
            "metadata": {
                "source_file": filename,
                "policy_title": policy_title,
                "doc_id": doc_id,
                "section_title": "Overview and Document Metadata",
                "category": category
            }
        })

    for i in range(1, len(sections), 2):
        sec_header = sections[i].replace("##", "").strip()
        sec_body = sections[i + 1].strip() if i + 1 < len(sections) else ""
        
        full_chunk_text = f"### {policy_title} - {sec_header}\n\n{sec_body}"
        
        chunks.append({
            "content": full_chunk_text,
            "metadata": {
                "source_file": filename,
                "policy_title": policy_title,
                "doc_id": doc_id,
                "section_title": sec_header,
                "category": category
            }
        })

    return chunks

def ingest_all_policies(docs_dir: Path = config.docs_dir, vector_store: Optional[HRVectorStore] = None) -> int:
    vs = vector_store or HRVectorStore()
    docs_path = Path(docs_dir)
    
    if not docs_path.exists():
        raise FileNotFoundError(f"Documents directory not found at: {docs_path}")

    md_files = list(docs_path.glob("*.md"))
    if not md_files:
        print(f"[!] No markdown files found in {docs_path}")
        return 0

    total_chunks = 0
    all_docs = []
    all_metas = []
    all_ids = []

    for file_path in md_files:
        chunks = parse_markdown_policy(file_path)
        base_id = file_path.stem
        for idx, chunk in enumerate(chunks):
            chunk_id = f"{base_id}_chunk_{idx}"
            all_docs.append(chunk["content"])
            all_metas.append(chunk["metadata"])
            all_ids.append(chunk_id)
        total_chunks += len(chunks)

    vs.add_chunks(documents=all_docs, metadatas=all_metas, ids=all_ids)
    print(f"[SUCCESS] Indexed {total_chunks} chunks into ChromaDB at: {vs.persist_dir}")
    return total_chunks

if __name__ == "__main__":
    ingest_all_policies()
