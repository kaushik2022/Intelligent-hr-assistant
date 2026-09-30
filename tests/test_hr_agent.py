"""
tests/test_hr_agent.py
Unit and integration tests for the Intelligent HR Assistant Agent,
Google ADK root_agent, ChromaDB vector store, document ingestion, and tools.
"""

import sys
import pytest
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Prevent module collisions when tests are run together
for mod in list(sys.modules.keys()):
    if mod == "src" or mod.startswith("src."):
        del sys.modules[mod]

from hr_agent.agent import root_agent
from hr_agent.vector_store import HRVectorStore
from hr_agent.ingest import ingest_all_policies, parse_markdown_policy
from hr_agent.tools import calculate_leave_entitlement, search_hr_policies, list_all_policy_documents

@pytest.fixture(scope="module")
def vector_store(tmp_path_factory):
    temp_dir = tmp_path_factory.mktemp("chroma")
    vs = HRVectorStore(persist_dir=temp_dir, collection_name="test_hr_policies")
    docs_dir = PROJECT_ROOT / "documents"
    ingest_all_policies(docs_dir=docs_dir, vector_store=vs)
    return vs

def test_markdown_chunking():
    doc_path = PROJECT_ROOT / "documents" / "leave_and_attendance_policy.md"
    chunks = parse_markdown_policy(doc_path)
    assert len(chunks) >= 4
    for c in chunks:
        assert "source_file" in c["metadata"]
        assert "section_title" in c["metadata"]
        assert "doc_id" in c["metadata"]

def test_vector_store_indexing_and_count(vector_store):
    count = vector_store.count()
    assert count >= 20

def test_vector_search_remote_work(vector_store):
    results = vector_store.search("How much is the home office setup stipend?", top_k=2)
    assert len(results) > 0
    top = results[0]
    assert "remote_and_hybrid_work_policy.md" in top["source"]
    assert "750" in top["content"] or "stipend" in top["content"].lower()

def test_vector_search_paternity_leave(vector_store):
    results = vector_store.search("paternity leave weeks for secondary caregiver", top_k=2)
    assert len(results) > 0
    content = results[0]["content"].lower()
    assert "parental" in content or "paternity" in content or "caregiver" in content

def test_google_adk_root_agent_properties():
    assert root_agent.name == "hr_agent"
    assert len(root_agent.tools) == 3
    tool_names = [getattr(t, "__name__", str(t)) for t in root_agent.tools]
    assert "search_hr_policies" in tool_names
    assert "list_all_policy_documents" in tool_names
    assert "calculate_leave_entitlement" in tool_names

def test_hr_agent_policy_search_tool():
    tool_output = search_hr_policies("What is the annual gym and fitness allowance?")
    assert "health_and_wellness_benefits.md" in tool_output
    assert "500" in tool_output

def test_leave_calculator_tool():
    pto_res = calculate_leave_entitlement("PTO", 6)
    assert "10.0 days" in pto_res or "accrued" in pto_res
    sick_res = calculate_leave_entitlement("sick")
    assert "10 paid sick days" in sick_res

def test_policy_catalog_tool():
    catalog = list_all_policy_documents()
    assert "leave_and_attendance_policy.md" in catalog
    assert "remote_and_hybrid_work_policy.md" in catalog
