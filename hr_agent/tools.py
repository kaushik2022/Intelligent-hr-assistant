"""
hr_agent/tools.py
Google ADK Tools for the Intelligent HR Assistant Agent.
Callable functions declared to the Google ADK Agent for semantic RAG retrieval,
policy inspection, and structured leave calculation.
"""

from typing import Optional
from pathlib import Path
from .vector_store import HRVectorStore
from .config import config

_vector_store: Optional[HRVectorStore] = None

def get_vector_store() -> HRVectorStore:
    global _vector_store
    if _vector_store is None:
        _vector_store = HRVectorStore()
    return _vector_store

def search_hr_policies(query: str, top_k: int = 3) -> str:
    """Search the company HR policy knowledge base in ChromaDB for policy guidelines, rules, and allowances.
    
    Args:
        query: The natural language question or keywords describing the policy inquiry.
        top_k: Number of relevant policy sections to retrieve (default is 3).

    Returns:
        A formatted string containing relevant policy excerpts with document citations.
    """
    vs = get_vector_store()
    results = vs.search(query=query, top_k=top_k)
    
    if not results:
        return "No matching HR policy records found in the local knowledge base."

    output = [f"Found {len(results)} relevant policy sections in Knowledge Base:"]
    for i, res in enumerate(results, 1):
        output.append(
            f"\n--- [Source {i}: {res['source']} | Section: {res['section']} | Relevance: {res['similarity_score']:.2f}] ---\n"
            f"{res['content']}\n"
        )
    return "\n".join(output)

def list_all_policy_documents() -> str:
    """Returns an inventory of all active enterprise HR policy documents available in the knowledge base."""
    docs_dir = config.docs_dir
    if not docs_dir.exists():
        return "No policy documents directory found."

    docs = list(docs_dir.glob("*.md"))
    if not docs:
        return "No policy documents found."

    lines = ["Active Company HR Policy Catalog:"]
    for d in docs:
        lines.append(f"- {d.name}")
    return "\n".join(lines)

def calculate_leave_entitlement(leave_type: str, months_worked: int = 12) -> str:
    """Calculates specific leave entitlement and accrual numbers based on company policy rules.
    
    Args:
        leave_type: The type of leave (e.g., 'PTO', 'Sick', 'Maternity', 'Paternity', 'Bereavement').
        months_worked: Number of months the employee has worked in the current calendar year.
    """
    lt = leave_type.lower()
    
    if "pto" in lt or "annual" in lt or "vacation" in lt:
        accrual_rate = 1.67
        accrued = round(min(20.0, months_worked * accrual_rate), 1)
        return (
            f"Annual PTO Calculation:\n"
            f"- Accrual rate: 1.67 days per month worked.\n"
            f"- For {months_worked} months of service: {accrued} days accrued (Max annual entitlement: 20 days).\n"
            f"- Rollover rule: Up to 5 unused days can roll over to Q1 (must be used by March 31)."
        )
    elif "sick" in lt or "medical" in lt:
        return (
            "Sick Leave Entitlement:\n"
            "- 10 paid sick days credited upfront annually on January 1.\n"
            "- Up to 2 consecutive days: No doctor note required.\n"
            "- 3+ consecutive days: Medical certificate required."
        )
    elif "maternity" in lt or "primary caregiver" in lt:
        return (
            "Primary Caregiver / Maternity Leave:\n"
            "- 26 weeks of 100% paid leave.\n"
            "- Followed by optional 4-week Gradual Return program (80% hours at 100% salary)."
        )
    elif "paternity" in lt or "secondary caregiver" in lt:
        return (
            "Secondary Caregiver / Paternity Leave:\n"
            "- 4 weeks of 100% paid leave.\n"
            "- Can be taken consecutively or in two 2-week blocks within the first 12 months."
        )
    elif "bereavement" in lt:
        return (
            "Bereavement Leave:\n"
            "- Up to 5 consecutive paid days for immediate family members.\n"
            "- Up to 3 consecutive paid days for extended family."
        )
    else:
        return f"Policy details for '{leave_type}' should be retrieved via `search_hr_policies('{leave_type}')`."
