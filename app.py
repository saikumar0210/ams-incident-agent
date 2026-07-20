"""
app.py

Entry point for the AMS Incident Agent FastAPI application.
Initializes the app, registers routes, and logs startup configuration.
"""
import uvicorn

from fastapi import FastAPI

from config import Config
from routes import router
from shared.logger import get_logger

# Logger scoped to this module
logger = get_logger("agent.app")

# Initialize the FastAPI application
app = FastAPI(
    title=Config.APPLICATION_NAME,
    version=Config.APPLICATION_VERSION,
    description="AI-powered incident analysis agent"
)

# Register all /agent routes
app.include_router(router)

# Log startup configuration
logger.info("[STEP 1] AMS Incident Agent starting up")
logger.info(f"[STEP 2] Environment : {Config.ENVIRONMENT}")
logger.info(f"[STEP 3] Groq Model  : {Config.GROQ_MODEL}")
logger.info(f"[STEP 4] Listening on : {Config.HOST}:{Config.PORT}")


# Health check endpoint
@app.get("/")
def home():
    return {
        "application": Config.APPLICATION_NAME,
        "version": Config.APPLICATION_VERSION,
        "environment": Config.ENVIRONMENT,
        "model": Config.GROQ_MODEL,
        "status": "Running"
    }


# Entry point when running directly
if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=Config.HOST,
        port=Config.PORT,
        reload=True
    )
