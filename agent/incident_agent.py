"""
agent/incident_agent.py

Core agent that analyzes an error log and decides whether to create an incident.

Flow:
    1. Receives AgentInput (log fields)
    2. Builds a structured prompt explaining the decision rules
    3. Calls Groq API with the prompt
    4. Parses the JSON response into AgentOutput
    5. Returns AgentOutput to the caller

Decision Rules (embedded in prompt):
    SKIP  - 4xx errors (user/client errors e.g. 400, 401, 403, 404, 422)
    CREATE - 5xx errors (server/system failures e.g. 500, 502, 503, 504)
    CREATE - OOM, connection failures, database errors, unhandled exceptions
"""
import json
import requests

from config import Config
from agent.models import AgentInput, AgentOutput
from shared.logger import get_logger

# Logger scoped to this agent
logger = get_logger("agent.incident_agent")


class IncidentAgent:

    def __init__(self):
        # Groq API endpoint for chat completions
        self.url = "https://api.groq.com/openai/v1/chat/completions"

        # Authorization header using the Groq API key from config
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {Config.GROQ_API_KEY}"
        }

        # Model to use for inference
        self.model = Config.GROQ_MODEL

        logger.info(f"[STEP 1] IncidentAgent initialized | Model : {self.model}")

    def analyze(self, input: AgentInput) -> AgentOutput:
        """
        Analyzes an error log and returns a decision on whether to create an incident.
        Falls back to creating the incident with original data if the Groq call fails.
        """
        logger.info(f"[STEP 1] Analyzing log | Service : {input.service} | Severity : {input.severity}")
        logger.info(f"[STEP 2] Error message : {input.message}")

        # Build the prompt with clear decision rules and expected JSON output format
        prompt = f"""
You are an intelligent incident management agent.

Your job is to analyze an error log and decide whether it requires creating an incident ticket.

## Decision Rules

SKIP the incident (should_create_incident = false) for:
- 400 Bad Request — user sent invalid data
- 401 Unauthorized — user is not authenticated
- 403 Forbidden — user does not have permission
- 404 Not Found — user hit a wrong URL
- 422 Unprocessable Entity — user sent invalid payload
- Any other client-side / user-caused errors

CREATE the incident (should_create_incident = true) for:
- 500 Internal Server Error — backend code crashed
- 501 Not Implemented — missing critical functionality
- 502 Bad Gateway — upstream service is down
- 503 Service Unavailable — server is overloaded or down
- 504 Gateway Timeout — service is too slow or unresponsive
- Out of Memory (OOM) errors
- Database connection failures or query errors
- Connection refused or connection timeout
- Unhandled exceptions or null pointer errors
- Any other server-side / system failures

## Error Log Details

Application   : {input.application}
Service       : {input.service}
Environment   : {input.environment}
Severity      : {input.severity}
Message       : {input.message}
Monitoring    : {input.monitoring_tool}

## Output Format

Respond ONLY with a valid JSON object. No explanation, no markdown, just JSON.

{{
  "should_create_incident": true or false,
  "error_type": "e.g. 500 Internal Server Error",
  "reason": "clear explanation of why this decision was made",
  "short_description": "concise incident title (only if should_create_incident is true, else null)",
  "description": "full enriched incident description (only if should_create_incident is true, else null)",
  "category": "Software or Network or Database (only if should_create_incident is true, else null)",
  "subcategory": "e.g. Application Error (only if should_create_incident is true, else null)",
  "impact": "1 for High, 2 for Medium, 3 for Low (only if should_create_incident is true, else null)",
  "urgency": "1 for High, 2 for Medium, 3 for Low (only if should_create_incident is true, else null)"
}}
"""

        try:
            logger.info("[STEP 3] Sending request to Groq API")

            # Call Groq chat completions API with the prompt
            response = requests.post(
                url=self.url,
                headers=self.headers,
                json={
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    # Low temperature for consistent, deterministic decisions
                    "temperature": 0.1
                },
                timeout=30
            )

            response.raise_for_status()
            logger.info(f"[STEP 4] Groq response received | Status : {response.status_code}")

            # Extract the text content from the Groq response
            content = (
                response.json()
                ["choices"][0]
                ["message"]
                ["content"]
            )

            logger.info(f"[STEP 5] Parsing agent decision")

            # Parse the JSON string returned by the model into AgentOutput
            parsed = json.loads(content)
            output = AgentOutput(**parsed)

            # Log the agent decision clearly for Render logs
            if output.should_create_incident:
                logger.info(f"[AGENT DECISION] CREATE INCIDENT")
                logger.info(f"[AGENT] Error Type : {output.error_type}")
                logger.info(f"[AGENT] Reason     : {output.reason}")
                logger.info(f"[AGENT] Impact     : {output.impact} | Urgency : {output.urgency}")
            else:
                logger.info(f"[AGENT DECISION] SKIP INCIDENT")
                logger.info(f"[AGENT] Error Type  : {output.error_type}")
                logger.info(f"[AGENT] Reason      : {output.reason}")
                logger.info(f"[AGENT] Service     : {input.service}")
                logger.info(f"[AGENT] Application : {input.application}")

            return output

        except Exception as ex:
            # If Groq call fails for any reason, fall back to creating the incident
            # with the original log data so no critical error is silently missed
            logger.error(f"[AGENT ERROR] Groq call failed : {ex}")
            logger.warning("[AGENT FALLBACK] Defaulting to create incident with original log data")

            return AgentOutput(
                should_create_incident=True,
                error_type=input.severity,
                reason="Agent unavailable — fallback to incident creation",
                short_description=input.message,
                description=(
                    f"Application : {input.application}\n\n"
                    f"Service : {input.service}\n\n"
                    f"Environment : {input.environment}\n\n"
                    f"Severity : {input.severity}\n\n"
                    f"Message : {input.message}\n\n"
                    f"Generated automatically from {input.monitoring_tool}."
                ),
                category="Software",
                impact="2",
                urgency="2"
            )
