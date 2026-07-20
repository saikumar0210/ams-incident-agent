"""
routes.py

Defines all API routes for the AMS Incident Agent.

Endpoints:
    POST /analyze-log - Accepts an error log, runs it through the agent,
                        returns a decision on whether to create an incident
"""
from fastapi import APIRouter

from agent.models import AgentInput, AgentOutput
from agent.incident_agent import IncidentAgent
from shared.logger import get_logger

# Logger scoped to this module
logger = get_logger("agent.routes")

# All routes grouped under /agent prefix
router = APIRouter(
    prefix="/agent",
    tags=["Incident Agent"]
)

# Single shared agent instance used by all requests
incident_agent = IncidentAgent()


# Accepts an error log, passes it to the agent, returns the decision
@router.post("/analyze-log", response_model=AgentOutput)
def analyze_log(input: AgentInput):
    logger.info(f"[REQUEST] POST /agent/analyze-log | Service : {input.service} | Message : {input.message}")

    # Run the log through the agent for analysis
    output = incident_agent.analyze(input)

    logger.info(f"[RESPONSE] POST /agent/analyze-log | Decision : {'CREATE' if output.should_create_incident else 'SKIP'}")
    return output
