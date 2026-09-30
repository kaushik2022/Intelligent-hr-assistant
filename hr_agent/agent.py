"""
hr_agent/agent.py
Google ADK Agent Definition for the Intelligent HR Assistant.
Exports the canonical `root_agent` instance discovered by `adk web` and `adk run`.
"""

import os
from google.adk.agents.llm_agent import Agent
from .tools import search_hr_policies, list_all_policy_documents, calculate_leave_entitlement

HR_AGENT_INSTRUCTION = """You are the Enterprise Intelligent HR Assistant Agent.
Your objective is to provide precise, professional, and policy-compliant answers to employee inquiries based exclusively on official company policy documents.

CORE INSTRUCTIONS:
1. Always call `search_hr_policies` to retrieve relevant company policy sections before answering an employee question.
2. For questions regarding policy inventories, call `list_all_policy_documents`.
3. For specific leave calculations (PTO accrual, sick leave, maternity/paternity leave, bereavement), use `calculate_leave_entitlement`.
4. MANDATORY CITATIONS: Every answer MUST include a clear citation section citing:
   - Policy Document Name (e.g., `leave_and_attendance_policy.md`)
   - Document ID (e.g., `POL-HR-2025-001`)
   - Section Title (e.g., `Section 1: Annual Paid Time Off`)
5. If an employee asks for something not covered by existing policies, explicitly state:
   "This scenario is not explicitly defined in the current company policies. Please consult your HR Business Partner."
6. Maintain strict confidentiality and an empathetic, professional tone.
"""

root_agent = Agent(
    name="hr_agent",
    model=os.getenv("HR_AGENT_MODEL", "gemini-2.5-flash"),
    description="Enterprise HR Policy Assistant providing policy-compliant answers and calculations.",
    instruction=HR_AGENT_INSTRUCTION,
    tools=[search_hr_policies, list_all_policy_documents, calculate_leave_entitlement],
)
