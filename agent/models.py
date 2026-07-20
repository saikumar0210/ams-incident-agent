"""
agent/models.py

Pydantic models for the Incident Agent.

Models:
    AgentInput  - Log fields sent to the agent for analysis
    AgentOutput - Agent decision returned after analyzing the log
"""
from typing import Optional
from pydantic import BaseModel


# Input sent to the agent — contains the raw error log fields
class AgentInput(BaseModel):

    application: str        # Name of the application that generated the log
    service: str            # Specific service or component
    environment: str        # e.g. production, staging
    severity: str           # e.g. ERROR, CRITICAL
    message: str            # The actual error message from the log
    monitoring_tool: str    # e.g. New Relic, Datadog


# Output returned by the agent after analyzing the log
class AgentOutput(BaseModel):

    should_create_incident: bool        # True = create incident, False = skip

    error_type: str                     # e.g. "500 Internal Server Error", "401 Unauthorized"

    reason: str                         # Why the agent made this decision

    # Fields below are only populated when should_create_incident is True
    short_description: Optional[str] = None     # Enriched incident title
    description: Optional[str] = None           # Enriched full incident details
    category: Optional[str] = None              # e.g. Software, Network
    subcategory: Optional[str] = None           # e.g. Application Error
    impact: Optional[str] = None                # 1=High, 2=Medium, 3=Low
    urgency: Optional[str] = None               # 1=High, 2=Medium, 3=Low
